# Verified CIFAR-10 main experiments
# Run only in a disposable clone or test copy of the repository.
# New round-log folders are timestamped under system\reproducibility_runs.
# Upstream PFLlib may still write model/result files outside -sfn.

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$systemDir = Join-Path $repoRoot "system"

if (-not (Test-Path (Join-Path $systemDir "main.py"))) {
    throw "Cannot find system\main.py. Keep this script under reproducibility\commands."
}

Write-Warning "Run this script only in a disposable clone or test copy."
$confirmation = Read-Host "Type YES to continue"
if ($confirmation -ne "YES") {
    Write-Host "Cancelled."
    exit 1
}

$stamp = Get-Date -Format "yyyyMMdd_HHmmss"
Set-Location $systemDir

function Invoke-SaugRun {
    param(
        [string]$Dataset,
        [int]$NumClasses,
        [string]$Goal,
        [string]$SaveFolder,
        [int]$Seed,
        [string]$Mode,
        [string[]]$ExtraArguments
    )

    $runArgs = @(
        "main.py",
        "-go", $Goal,
        "-sfn", $SaveFolder,
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
        "--ld_mode", $Mode,
        "--ld_verbose", "0",
        "--comm_base_cost", "1.0",
        "--comm_penalty_scale", "5.0"
    )

    if ($ExtraArguments) {
        $runArgs += $ExtraArguments
    }

    Write-Host ""
    Write-Host "=================================================="
    Write-Host "Dataset=$Dataset Mode=$Mode Seed=$Seed"
    Write-Host "Output=$SaveFolder"
    Write-Host "=================================================="

    & python @runArgs

    if ($LASTEXITCODE -ne 0) {
        throw "Run failed: Dataset=$Dataset Mode=$Mode Seed=$Seed"
    }
}

$outputRoot = Join-Path $systemDir "reproducibility_runs\$stamp\cifar10_main"

foreach ($seed in 0,1,2,3,4) {
    Invoke-SaugRun `
        -Dataset "Cifar10" `
        -NumClasses 10 `
        -Goal "verified_C10_off_seed$seed" `
        -SaveFolder (Join-Path $outputRoot "off") `
        -Seed $seed `
        -Mode "off" `
        -ExtraArguments @()
}

foreach ($seed in 0,1,2,3,4) {
    Invoke-SaugRun `
        -Dataset "Cifar10" `
        -NumClasses 10 `
        -Goal "verified_C10_speed_seed$seed" `
        -SaveFolder (Join-Path $outputRoot "speed") `
        -Seed $seed `
        -Mode "speed" `
        -ExtraArguments @("--ld_speed_threshold", "100.0")
}

foreach ($tau in 0.4,0.5,0.6,0.7) {
    foreach ($seed in 0,1,2,3,4) {
        Invoke-SaugRun `
            -Dataset "Cifar10" `
            -NumClasses 10 `
            -Goal "verified_C10_saug_tau${tau}_seed$seed" `
            -SaveFolder (Join-Path $outputRoot "saug_tau$tau") `
            -Seed $seed `
            -Mode "score" `
            -ExtraArguments @(
                "--ld_alpha", "0.5",
                "--ld_beta", "0.3",
                "--ld_gamma", "0.2",
                "--ld_tau", "$tau",
                "--ld_v_max", "120.0",
                "--ld_k_max", "5.0"
            )
    }
}

Write-Host ""
Write-Host "Finished. New logs are under:"
Write-Host $outputRoot
