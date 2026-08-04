import numpy as np
import time
from flcore.clients.clientbase import Client
from utils.data_utils import read_client_data
from utils.ALA import ALA


class clientALA(Client):
    def __init__(self, args, id, train_samples, test_samples, **kwargs):
        super().__init__(args, id, train_samples, test_samples, **kwargs)

        self.eta = args.eta
        self.rand_percent = args.rand_percent
        self.layer_idx = args.layer_idx

        train_data = read_client_data(
            self.dataset, self.id, is_train=True, few_shot=self.few_shot
        )
        self.ALA = ALA(
            self.id,
            self.loss,
            train_data,
            self.batch_size,
            self.rand_percent,
            self.layer_idx,
            self.eta,
            self.device
        )

        self.seed = getattr(args, "seed", 0)
        # =========================================
        # Link-Drop（断链）参数
        # =========================================
        self.ld_mode = getattr(args, "ld_mode", "off")   # off / speed / score
        self.ld_alpha = getattr(args, "ld_alpha", 0.5)   # speed weight（速度权重）
        self.ld_beta = getattr(args, "ld_beta", 0.3)     # link weight（链路权重）
        self.ld_gamma = getattr(args, "ld_gamma", 0.2)   # staleness weight（陈旧度权重）
        self.ld_use_speed = getattr(args, "ld_use_speed", 1)
        self.ld_use_link = getattr(args, "ld_use_link", 1)
        self.ld_use_stale = getattr(args, "ld_use_stale", 1)
        self.ld_tau = getattr(args, "ld_tau", 0.5)       # score threshold（分数阈值）
        self.ld_v_max = getattr(args, "ld_v_max", 120.0) # max speed（最大参考速度）
        self.ld_k_max = getattr(args, "ld_k_max", 5.0)   # max staleness（最大参考陈旧度）
        self.ld_speed_threshold = getattr(args, "ld_speed_threshold", 100.0)

        # =========================================
        # Random-Gate 随机上传基线
        # =========================================
        self.random_upload_ratio = float(
            getattr(args, "random_upload_ratio", 0.5)
        )
        self.random_upload_ratio = float(
            np.clip(self.random_upload_ratio, 0.0, 1.0)
        )

        # Random-Gate 使用单独的随机数生成器。
        # 不与 speed/link trace 共用 rng，防止随机上传决策受到轨迹生成过程影响。
        self.random_gate_rng = np.random.RandomState(
            self.seed * 1000003 + self.id * 9176 + 12345
        )

        self.ld_verbose = bool(getattr(args, "ld_verbose", 0))

        # =========================================
        # Communication cost（通信代价）参数
        # 统一通信代价模型，不 sleep，只统计 cost
        # cost = base + scale * (1 - link_quality)
        # =========================================
        self.comm_base_cost = getattr(args, "comm_base_cost", 1.0)
        self.comm_penalty_scale = getattr(args, "comm_penalty_scale", 5.0)

        self.global_rounds = getattr(args, "global_rounds", 200)


        # =========================================
        # 客户端状态
        # =========================================
        self.staleness = 0
        self.connected = True
        self.should_upload = True
        self.current_round = 0

        self.last_score = 0.0
        self.last_speed = 0.0
        self.last_link = 1.0

        # 通信代价统计
        self.round_comm_cost = 0.0
        self.total_comm_cost = 0.0

        # 每个客户端自己的随机状态，保证可复现
        self.rng = np.random.RandomState(self.seed + self.id)

        # 预生成 speed trace（速度轨迹）和 link trace（链路质量轨迹）
        self.speed_trace, self.link_trace = self._build_traces(self.global_rounds + 5)

    def _build_traces(self, total_rounds):
        """
        构造每个客户端每一轮的：
        1) speed trace（速度轨迹）
        2) link trace（链路质量轨迹）
        """
        speeds = []
        links = []

        v = self.rng.uniform(20, 60)

        for _ in range(total_rounds):
            # random walk（随机游走）
            v = np.clip(v + self.rng.normal(0, 10), 0, self.ld_v_max)

            # link quality（链路质量），速度越高平均越差
            q = np.clip(1.0 - 0.8 * (v / self.ld_v_max) + self.rng.normal(0, 0.05), 0.0, 1.0)

            speeds.append(float(v))
            links.append(float(q))

        return speeds, links

    def compute_linkdrop_score(self, round_idx):
        """
        自适应断链分数（支持消融）：
        score = alpha * speed_norm + beta * (1 - link_norm) + gamma * stale_norm
        其中某一项可以通过开关关闭；关闭后其权重置零，并对剩余权重重归一化
        """
        v = self.speed_trace[round_idx]
        q = self.link_trace[round_idx]

        v_norm = min(v / self.ld_v_max, 1.0)
        q_norm = min(max(q, 0.0), 1.0)
        s_norm = min(self.staleness / self.ld_k_max, 1.0)

        w_v = self.ld_alpha if self.ld_use_speed else 0.0
        w_q = self.ld_beta if self.ld_use_link else 0.0
        w_s = self.ld_gamma if self.ld_use_stale else 0.0

        w_sum = w_v + w_q + w_s
        if w_sum <= 0:
            score = 0.0
        else:
            w_v /= w_sum
            w_q /= w_sum
            w_s /= w_sum

            score = (
                    w_v * v_norm +
                    w_q * (1.0 - q_norm) +
                    w_s * s_norm
            )

        return score, v, q, s_norm

    def estimate_upload_comm_cost(self):
        """
        统一通信代价模型（Unified Communication Cost Model / 统一通信代价模型）

        若本轮上传：
            cost = base_cost + penalty_scale * (1 - link_quality)
        若本轮不上传：
            cost = 0
        """
        if not self.should_upload:
            return 0.0

        round_idx = min(max(self.current_round, 0), len(self.link_trace) - 1)
        q = self.link_trace[round_idx]
        q = min(max(q, 0.0), 1.0)

        cost = self.comm_base_cost + self.comm_penalty_scale * (1.0 - q)
        return float(cost)

    def train(self):
        """
        本地训练（local training / 本地训练）
        注意：
        - connected（连接状态）时：先执行 ALA，再本地训练
        - dropped / local-only（断链状态）时：不执行 ALA，只本地训练
        """
        trainloader = self.load_train_data()
        self.model.train()

        start_time = time.time()
        self.round_comm_cost = 0.0

        max_local_epochs = self.local_epochs
        if self.train_slow:
            max_local_epochs = np.random.randint(1, max(2, max_local_epochs // 2))

        for epoch in range(max_local_epochs):
            for i, (x, y) in enumerate(trainloader):
                if type(x) == type([]):
                    x[0] = x[0].to(self.device)
                else:
                    x = x.to(self.device)
                y = y.to(self.device)

                if self.train_slow:
                    time.sleep(0.1 * np.abs(np.random.rand()))

                output = self.model(x)
                loss = self.loss(output, y)
                self.optimizer.zero_grad()
                loss.backward()
                self.optimizer.step()

        # 不 sleep，只记录通信代价
        self.round_comm_cost = self.estimate_upload_comm_cost()
        self.total_comm_cost += self.round_comm_cost

        if self.learning_rate_decay:
            self.learning_rate_scheduler.step()

        self.train_time_cost['num_rounds'] += 1
        self.train_time_cost['total_cost'] += time.time() - start_time

        self.current_round += 1

    def local_initialization(self, received_global_model):
        """
        每轮本地训练前执行上传门控判断。

        模式：
        - off:
            原始 FedALA，所有被选中的客户端均上传。
        - speed:
            仅根据速度阈值决定是否上传。
        - score:
            根据 speed、link quality、staleness 综合评分决定是否上传。
        - random:
            不使用任何状态信息，以固定概率随机决定是否上传。
        """
        round_idx = min(
            self.current_round,
            len(self.speed_trace) - 1
        )

        vehicle_speed = self.speed_trace[round_idx]
        link_quality = self.link_trace[round_idx]
        score, _, _, _ = self.compute_linkdrop_score(round_idx)

        self.last_speed = vehicle_speed
        self.last_link = link_quality
        self.last_score = score

        # 每轮先恢复默认状态，避免沿用上一轮结果。
        self.connected = True
        self.should_upload = True

        # =====================================================
        # 模式 1：Off，原始 FedALA
        # =====================================================
        if self.ld_mode == "off":
            self.connected = True
            self.should_upload = True

            self.ALA.adaptive_local_aggregation(
                received_global_model,
                self.model
            )

            if self.ld_verbose:
                print(
                    f"[Client {self.id}] Round {round_idx} | "
                    f"mode=off -> UPLOAD"
                )

            return True

        # =====================================================
        # 模式 2：Speed，仅使用速度阈值
        # =====================================================
        elif self.ld_mode == "speed":
            if vehicle_speed > self.ld_speed_threshold:
                self.connected = False
                self.should_upload = False
                self.staleness += 1

                if self.ld_verbose:
                    print(
                        f"[Client {self.id}] Round {round_idx} | "
                        f"mode=speed, "
                        f"speed={vehicle_speed:.3f}, "
                        f"threshold={self.ld_speed_threshold:.3f} "
                        f"-> LOCAL-ONLY"
                    )

                return False

            self.connected = True
            self.should_upload = True

            self.ALA.adaptive_local_aggregation(
                received_global_model,
                self.model
            )

            if self.ld_verbose:
                print(
                    f"[Client {self.id}] Round {round_idx} | "
                    f"mode=speed, "
                    f"speed={vehicle_speed:.3f}, "
                    f"threshold={self.ld_speed_threshold:.3f} "
                    f"-> UPLOAD"
                )

            return True

        # =====================================================
        # 模式 3：Score，SAUG 状态感知门控
        # =====================================================
        elif self.ld_mode == "score":
            if score > self.ld_tau:
                self.connected = False
                self.should_upload = False
                self.staleness += 1

                if self.ld_verbose:
                    print(
                        f"[Client {self.id}] Round {round_idx} | "
                        f"mode=score, "
                        f"speed={vehicle_speed:.3f}, "
                        f"link={link_quality:.3f}, "
                        f"staleness={self.staleness}, "
                        f"score={score:.3f}, "
                        f"tau={self.ld_tau:.3f} "
                        f"-> LOCAL-ONLY"
                    )

                return False

            self.connected = True
            self.should_upload = True

            self.ALA.adaptive_local_aggregation(
                received_global_model,
                self.model
            )

            if self.ld_verbose:
                print(
                    f"[Client {self.id}] Round {round_idx} | "
                    f"mode=score, "
                    f"speed={vehicle_speed:.3f}, "
                    f"link={link_quality:.3f}, "
                    f"staleness={self.staleness}, "
                    f"score={score:.3f}, "
                    f"tau={self.ld_tau:.3f} "
                    f"-> UPLOAD"
                )

            return True

        # =====================================================
        # 模式 4：Random-Gate
        # =====================================================
        elif self.ld_mode == "random":
            random_value = float(self.random_gate_rng.rand())

            if random_value < self.random_upload_ratio:
                self.connected = True
                self.should_upload = True

                # 与 SAUG 中 upload 客户端保持相同流程：
                # 执行 ALA 后进行本地训练并上传。
                self.ALA.adaptive_local_aggregation(
                    received_global_model,
                    self.model
                )

                if self.ld_verbose:
                    print(
                        f"[Client {self.id}] Round {round_idx} | "
                        f"mode=random, "
                        f"draw={random_value:.6f}, "
                        f"upload_ratio={self.random_upload_ratio:.6f} "
                        f"-> UPLOAD"
                    )

                return True

            self.connected = False
            self.should_upload = False
            self.staleness += 1

            if self.ld_verbose:
                print(
                    f"[Client {self.id}] Round {round_idx} | "
                    f"mode=random, "
                    f"draw={random_value:.6f}, "
                    f"upload_ratio={self.random_upload_ratio:.6f} "
                    f"-> LOCAL-ONLY"
                )

            return False

        # =====================================================
        # 未识别模式：安全回退到 Off
        # =====================================================
        else:
            self.connected = True
            self.should_upload = True

            self.ALA.adaptive_local_aggregation(
                received_global_model,
                self.model
            )

            if self.ld_verbose:
                print(
                    f"[Client {self.id}] Round {round_idx} | "
                    f"unknown mode={self.ld_mode} -> UPLOAD"
                )

            return True