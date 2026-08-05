# Reconstructed fixed-threshold state-factor ablations
# Common threshold: tau = 0.5
# Run only in a disposable clone or test copy of the repository.

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$systemDir = Join-Path $repoRoot "system"

if (-not (Test-Path (Join-Path $systemDir "main.py"))) {
    throw "Cannot find system\main.py. Keep this script under reproducibility\commands."
}

Write-Warning "Run this script only in a disposable clone or test copy."
Write-Warning "This is the reconstructed fixed-tau=0.5 ablation configuration."
$confirmation = Read-Host "Type YES to continue"
if ($confirmation -ne "YES") {
    Write-Host "Cancelled."
    exit 1
}

$stamp = Get-Date -Format "yyyyMMdd_HHmmss"
Set-Location $systemDir

function Invoke-AblationRun {
    param(
        [string]$Dataset,
        [int]$NumClasses,
        [string]$VariantName,
        [int]$Seed,
        [int]$UseSpeed,
        [int]$UseLink,
        [int]$UseStale
    )

    $outputRoot = Join-Path $systemDir "reproducibility_runs\$stamp\ablation_fixed_tau05\$Dataset\$VariantName"
    $goal = "ablation_fixed_tau05_${Dataset}_${VariantName}_seed$Seed"

    $runArgs = @(
        "main.py",
        "-go", $goal,
        "-sfn", $outputRoot,
        "-algo", "FedALA",
        "-data", $Dataset,
        "-ncl", "$NumClasses",
        "-m", "CNN",
        "-gr", "50",
        "-nc", "20",
        "-jr", "1.0",
        "-t", "1",
        "-lbs", "10",
        "-lr", "0.005",
        "-ls", "1",
        "-eg", "1",
        "-et", "1.0",
        "-s", "80",
        "-p", "2",
        "-dev", "cuda",
        "-did", "0",
        "--seed", "$Seed",
        "--ld_mode", "score",
        "--ld_alpha", "0.5",
        "--ld_beta", "0.3",
        "--ld_gamma", "0.2",
        "--ld_use_speed", "$UseSpeed",
        "--ld_use_link", "$UseLink",
        "--ld_use_stale", "$UseStale",
        "--ld_tau", "0.5",
        "--ld_v_max", "120.0",
        "--ld_k_max", "5.0",
        "--ld_verbose", "0",
        "--comm_base_cost", "1.0",
        "--comm_penalty_scale", "5.0"
    )

    Write-Host ""
    Write-Host "=================================================="
    Write-Host "Dataset=$Dataset Variant=$VariantName Seed=$Seed"
    Write-Host "Switches: speed=$UseSpeed link=$UseLink stale=$UseStale"
    Write-Host "tau=0.5"
    Write-Host "Output=$outputRoot"
    Write-Host "=================================================="

    & python @runArgs

    if ($LASTEXITCODE -ne 0) {
        throw "Run failed: Dataset=$Dataset Variant=$VariantName Seed=$Seed"
    }
}

$variants = @(
    @{ Name = "full";         Speed = 1; Link = 1; Stale = 1 },
    @{ Name = "wo_link";      Speed = 1; Link = 0; Stale = 1 },
    @{ Name = "wo_speed";     Speed = 0; Link = 1; Stale = 1 },
    @{ Name = "wo_staleness"; Speed = 1; Link = 1; Stale = 0 }
)

foreach ($datasetInfo in @(
    @{ Dataset = "Cifar10";  NumClasses = 10  },
    @{ Dataset = "Cifar100"; NumClasses = 100 }
)) {
    foreach ($variant in $variants) {
        foreach ($seed in 0,1,2,3,4) {
            Invoke-AblationRun `
                -Dataset $datasetInfo.Dataset `
                -NumClasses $datasetInfo.NumClasses `
                -VariantName $variant.Name `
                -Seed $seed `
                -UseSpeed $variant.Speed `
                -UseLink $variant.Link `
                -UseStale $variant.Stale
        }
    }
}

Write-Host ""
Write-Host "All reconstructed fixed-threshold ablations finished."
Write-Host "New outputs are under:"
Write-Host (Join-Path $systemDir "reproducibility_runs\$stamp\ablation_fixed_tau05")
