# Two-round smoke test
# Run only in a disposable clone or test copy.
# This script does not reproduce manuscript results.

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$systemDir = Join-Path $repoRoot "system"

if (-not (Test-Path (Join-Path $systemDir "main.py"))) {
    throw "Cannot find system\main.py."
}

Write-Warning "This smoke test may still update model/result files created by upstream PFLlib."
$confirmation = Read-Host "Type YES to continue in a disposable clone"
if ($confirmation -ne "YES") {
    Write-Host "Cancelled."
    exit 1
}

$stamp = Get-Date -Format "yyyyMMdd_HHmmss"
$outputRoot = Join-Path $systemDir "reproducibility_runs\$stamp\smoke_test"

Set-Location $systemDir

$runArgs = @(
    "main.py",
    "-go", "smoke_C10_saug_seed999",
    "-sfn", $outputRoot,
    "-algo", "FedALA",
    "-data", "Cifar10",
    "-ncl", "10",
    "-m", "CNN",
    "-gr", "2",
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
    "--seed", "999",
    "--ld_mode", "score",
    "--ld_alpha", "0.5",
    "--ld_beta", "0.3",
    "--ld_gamma", "0.2",
    "--ld_tau", "0.5",
    "--ld_v_max", "120.0",
    "--ld_k_max", "5.0",
    "--ld_verbose", "0",
    "--comm_base_cost", "1.0",
    "--comm_penalty_scale", "5.0"
)

& python @runArgs

if ($LASTEXITCODE -ne 0) {
    throw "Smoke test failed."
}

Write-Host ""
Write-Host "Smoke test finished. Check:"
Write-Host $outputRoot
