import os
import csv
import time
import matplotlib.pyplot as plt

from flcore.clients.clientala import clientALA
from flcore.servers.serverbase import Server


class FedALA(Server):
    def __init__(self, args, times):
        super().__init__(args, times)

        self.set_slow_clients()
        self.set_clients(clientALA)

        print(f"\nJoin ratio / total clients: {self.join_ratio} / {self.num_clients}")
        print("Finished creating server and clients（服务器和客户端创建完成）.")

        self.Budget = []
        self.CommBudget = []
        self.round_logs = []

        self.ld_mode = getattr(args, "ld_mode", "off")
        self.ld_tau = getattr(args, "ld_tau", 0.5)
        self.random_upload_ratio = float(
            getattr(args, "random_upload_ratio", 0.5)
        )
        self.seed = getattr(args, "seed", 0)
        self.log_root = getattr(args, "save_folder_name", "items")

    def _get_exp_dir(self):
        if self.ld_mode == "random":
            exp_name = (
                f"{self.dataset}_{self.algorithm}_"
                f"random_p{self.random_upload_ratio}_"
                f"seed{self.seed}"
            )
        elif self.ld_mode == "score":
            exp_name = (
                f"{self.dataset}_{self.algorithm}_"
                f"score_tau{self.ld_tau}_"
                f"seed{self.seed}"
            )
        elif self.ld_mode == "speed":
            exp_name = (
                f"{self.dataset}_{self.algorithm}_"
                f"speed_seed{self.seed}"
            )
        else:
            exp_name = (
                f"{self.dataset}_{self.algorithm}_"
                f"off_seed{self.seed}"
            )

        exp_dir = os.path.join(
            self.log_root,
            "linkdrop_logs",
            exp_name
        )

        os.makedirs(exp_dir, exist_ok=True)
        return exp_dir

    def _save_round_logs_csv(self):
        if len(self.round_logs) == 0:
            return

        exp_dir = self._get_exp_dir()
        csv_path = os.path.join(exp_dir, "round_log.csv")

        fieldnames = [
            "round",
            "current_eval_acc",
            "best_acc_so_far",
            "round_comm_cost",
            "total_comm_cost",
            "selected",
            "upload",
            "dropped",
            "runtime_sec",
            "ld_mode",
            "ld_tau",
            "random_upload_ratio",
            "seed"
        ]

        with open(csv_path, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for row in self.round_logs:
                writer.writerow(row)

        print(f"[Saved] round log -> {csv_path}")

    def _plot_accuracy_curve(self):
        if len(self.round_logs) == 0:
            return

        exp_dir = self._get_exp_dir()
        save_path = os.path.join(exp_dir, "accuracy_curve.png")

        rounds = [row["round"] for row in self.round_logs]
        current_acc = [
            row["current_eval_acc"] if row["current_eval_acc"] is not None else 0.0
            for row in self.round_logs
        ]
        best_acc = [row["best_acc_so_far"] for row in self.round_logs]

        plt.figure(figsize=(8, 5))
        plt.plot(rounds, current_acc, label="Current Eval Accuracy")
        plt.plot(rounds, best_acc, label="Best Accuracy So Far")
        plt.xlabel("Round")
        plt.ylabel("Accuracy")
        plt.title(f"Accuracy Curve ({self.ld_mode}, tau={self.ld_tau}, seed={self.seed})")
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(save_path, dpi=200)
        plt.close()

        print(f"[Saved] accuracy curve -> {save_path}")

    def _plot_comm_curve(self):
        if len(self.round_logs) == 0:
            return

        exp_dir = self._get_exp_dir()
        save_path = os.path.join(exp_dir, "comm_curve.png")

        rounds = [row["round"] for row in self.round_logs]
        round_comm = [row["round_comm_cost"] for row in self.round_logs]
        total_comm = [row["total_comm_cost"] for row in self.round_logs]

        plt.figure(figsize=(8, 5))
        plt.plot(rounds, round_comm, label="Round Comm Cost")
        plt.plot(rounds, total_comm, label="Total Comm Cost")
        plt.xlabel("Round")
        plt.ylabel("Communication Cost")
        plt.title(f"Communication Cost Curve ({self.ld_mode}, tau={self.ld_tau}, seed={self.seed})")
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(save_path, dpi=200)
        plt.close()

        print(f"[Saved] communication curve -> {save_path}")

    def _plot_participation_curve(self):
        if len(self.round_logs) == 0:
            return

        exp_dir = self._get_exp_dir()
        save_path = os.path.join(exp_dir, "participation_curve.png")

        rounds = [row["round"] for row in self.round_logs]
        upload = [row["upload"] for row in self.round_logs]
        dropped = [row["dropped"] for row in self.round_logs]

        plt.figure(figsize=(8, 5))
        plt.plot(rounds, upload, label="Upload Clients")
        plt.plot(rounds, dropped, label="Dropped Clients")
        plt.xlabel("Round")
        plt.ylabel("Client Count")
        plt.title(f"Participation Curve ({self.ld_mode}, tau={self.ld_tau}, seed={self.seed})")
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(save_path, dpi=200)
        plt.close()

        print(f"[Saved] participation curve -> {save_path}")

    def _save_all_artifacts(self):
        self._save_round_logs_csv()
        self._plot_accuracy_curve()
        self._plot_comm_curve()
        self._plot_participation_curve()

    def train(self):
        last_eval_acc = None
        best_acc_so_far = 0.0
        total_comm_cost = 0.0

        # 改这里：只跑 global_rounds 轮，而不是 global_rounds + 1
        for i in range(self.global_rounds):
            s_t = time.time()

            # 1) 选择本轮客户端
            self.selected_clients = self.select_clients()

            # 2) 给本轮选中的客户端发送模型，并让客户端决定是否断链
            self.send_models()

            # 3) 评估
            if i % self.eval_gap == 0:
                print(f"\n-------------Round number（轮次）: {i}-------------")
                print("\nEvaluate global model（评估全局模型）")
                self.evaluate()

                if len(self.rs_test_acc) > 0:
                    last_eval_acc = float(self.rs_test_acc[-1])
                    best_acc_so_far = max(best_acc_so_far, last_eval_acc)

            # 4) 所有被选中的客户端都先本地训练
            for client in self.selected_clients:
                client.train()

            # 5) 统计本轮通信代价
            round_comm_cost = 0.0
            for client in self.selected_clients:
                round_comm_cost += getattr(client, "round_comm_cost", 0.0)

            self.CommBudget.append(round_comm_cost)
            total_comm_cost += round_comm_cost

            # 6) 只保留本轮允许上传的客户端
            active_clients = []
            dropped_clients = []

            for client in self.selected_clients:
                if getattr(client, "should_upload", True):
                    active_clients.append(client)
                    client.staleness = 0
                else:
                    dropped_clients.append(client)

            print(
                f"[Round {i}] selected（选中）={len(self.selected_clients)}, "
                f"upload（上传）={len(active_clients)}, "
                f"dropped（断链）={len(dropped_clients)}"
            )
            print(
                f"[Round {i}] emulated communication cost（仿真通信代价）={round_comm_cost:.4f}"
            )

            self.selected_clients = active_clients
            self.current_num_join_clients = len(self.selected_clients)

            # 7) 聚合
            if len(self.selected_clients) > 0:
                self.receive_models()

                if self.dlg_eval and i % self.dlg_gap == 0:
                    self.call_dlg(i)

                self.aggregate_parameters()
            else:
                print(f"[Round {i}] No client uploaded models（本轮没有客户端上传，跳过聚合）.")

            # 8) 记录运行时间
            runtime_sec = time.time() - s_t
            self.Budget.append(runtime_sec)
            print('-' * 25, 'time cost（程序运行时间，仅参考）', '-' * 25, runtime_sec)

            # 9) 记录每轮日志
            self.round_logs.append({
                "round": i,
                "current_eval_acc": last_eval_acc,
                "best_acc_so_far": best_acc_so_far,
                "round_comm_cost": round_comm_cost,
                "total_comm_cost": total_comm_cost,
                "selected": len(active_clients) + len(dropped_clients),
                "upload": len(active_clients),
                "dropped": len(dropped_clients),
                "runtime_sec": runtime_sec,
                "ld_mode": self.ld_mode,
                "ld_tau": self.ld_tau,
                "random_upload_ratio": self.random_upload_ratio,
                "seed": self.seed
            })

            if self.auto_break and self.check_done(acc_lss=[self.rs_test_acc], top_cnt=self.top_cnt):
                break

        print("\nBest accuracy（最佳精度）.")
        print(max(self.rs_test_acc))

        print("\nAverage runtime per round（每轮平均程序运行时间，仅参考）.")
        print(sum(self.Budget) / max(len(self.Budget), 1))

        print("\nAverage emulated communication cost per round（每轮平均仿真通信代价）.")
        print(sum(self.CommBudget) / max(len(self.CommBudget), 1))

        print("\nTotal emulated communication cost（总仿真通信代价）.")
        print(sum(self.CommBudget))

        # 保存原有结果
        self.save_results()
        self.save_global_model()

        # 保存新增日志和图
        self._save_all_artifacts()

        if self.num_new_clients > 0:
            self.eval_new_clients = True
            self.set_new_clients(clientALA)
            print(f"\n-------------Fine tuning round（微调轮）-------------")
            print("\nEvaluate new clients（评估新客户端）")
            self.evaluate()

    def send_models(self):
        assert len(self.clients) > 0

        for client in self.selected_clients:
            client.local_initialization(self.global_model)