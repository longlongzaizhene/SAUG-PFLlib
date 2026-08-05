# Verified matched Random-Gate experiments
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

$outputRoot = Join-Path $systemDir "reproducibility_runs\$stamp\random_gate"

foreach ($seed in 0,1,2,3,4) {
    Invoke-SaugRun `
        -Dataset "Cifar10" `
        -NumClasses 10 `
        -Goal "verified_randomGate_C10_p05398_seed$seed" `
        -SaveFolder (Join-Path $outputRoot "Cifar10_p05398") `
        -Seed $seed `
        -Mode "random" `
        -ExtraArguments @("--random_upload_ratio", "0.5398")
}

foreach ($seed in 0,1,2,3,4) {
    Invoke-SaugRun `
        -Dataset "Cifar100" `
        -NumClasses 100 `
        -Goal "verified_randomGate_C100_p09156_seed$seed" `
        -SaveFolder (Join-Path $outputRoot "Cifar100_p09156") `
        -Seed $seed `
        -Mode "random" `
        -ExtraArguments @("--random_upload_ratio", "0.9156")
}

Write-Host ""
Write-Host "Finished. New logs are under:"
Write-Host $outputRoot
