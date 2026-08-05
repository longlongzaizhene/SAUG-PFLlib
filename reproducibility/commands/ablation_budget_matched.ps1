param(
    [string]$ThresholdCsv = ""
)

$ErrorActionPreference = "Stop"
$InvariantCulture = [System.Globalization.CultureInfo]::InvariantCulture

# Locate the repository from reproducibility\commands.
$repoRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$systemDir = Join-Path $repoRoot "system"

if (-not (Test-Path -LiteralPath (Join-Path $systemDir "main.py"))) {
    throw "Cannot find system\main.py. Keep this script under reproducibility\commands."
}

if ([string]::IsNullOrWhiteSpace($ThresholdCsv)) {
    $ThresholdCsv = Join-Path $repoRoot "reproducibility\configs\budget_matched_thresholds.csv"
}

if (-not (Test-Path -LiteralPath $ThresholdCsv)) {
    throw ("Threshold CSV was not found: {0}" -f $ThresholdCsv)
}

$ThresholdCsv = (Resolve-Path -LiteralPath $ThresholdCsv).Path
$thresholdRows = Import-Csv -LiteralPath $ThresholdCsv

$variants = @("wolink", "wospeed", "wostale")

foreach ($variant in $variants) {
    $matchedRow = $thresholdRows |
        Where-Object { $_.variant -eq $variant } |
        Select-Object -First 1

    if ($null -eq $matchedRow) {
        throw ("Threshold CSV is missing variant: {0}" -f $variant)
    }
}

Write-Warning "Run this script only in a disposable clone or test copy."
Write-Host "This script launches 30 full experiments."
$confirmation = Read-Host "Type YES to continue"
if ($confirmation -ne "YES") {
    Write-Host "Cancelled."
    exit 1
}

$stamp = Get-Date -Format "yyyyMMdd_HHmmss"
$runRoot = Join-Path $systemDir "reproducibility_runs\$stamp\ablation_budget_matched"
$consoleLogRoot = Join-Path $runRoot "console_logs"

New-Item -ItemType Directory -Path $runRoot -Force | Out-Null
New-Item -ItemType Directory -Path $consoleLogRoot -Force | Out-Null
Copy-Item -LiteralPath $ThresholdCsv -Destination (Join-Path $runRoot "budget_matched_thresholds.csv")

$manifestPath = Join-Path $runRoot "run_manifest.csv"
$manifest = @()

$datasets = @(
    [PSCustomObject]@{ Name = "Cifar10"; NumClasses = 10 },
    [PSCustomObject]@{ Name = "Cifar100"; NumClasses = 100 }
)

$totalRuns = 30
$runIndex = 0

Write-Host ""
Write-Host ("Threshold CSV : {0}" -f $ThresholdCsv)
Write-Host ("Result root   : {0}" -f $runRoot)
Write-Host ("Total runs    : {0}" -f $totalRuns)
Write-Host "Archived experiment directories will not be modified."
Write-Host ""

Set-Location $systemDir

foreach ($dataset in $datasets) {
    foreach ($variant in $variants) {
        $row = $thresholdRows |
            Where-Object { $_.variant -eq $variant } |
            Select-Object -First 1

        $tauValue = [double]::Parse([string]$row.matched_tau, $InvariantCulture)
        $tauText = $tauValue.ToString("0.00000", $InvariantCulture)

        $useSpeed = [int]$row.ld_use_speed
        $useLink = [int]$row.ld_use_link
        $useStale = [int]$row.ld_use_stale

        $saveFolder = Join-Path $runRoot "$($dataset.Name)\$variant"
        New-Item -ItemType Directory -Path $saveFolder -Force | Out-Null

        foreach ($seed in @(0, 1, 2, 3, 4)) {
            $runIndex += 1

            $goal = "bm_${stamp}_$($dataset.Name)_${variant}_seed${seed}"
            $consoleLogPath = Join-Path $consoleLogRoot "$($dataset.Name)_${variant}_seed${seed}.log"

            $pythonArgs = @(
                "main.py",
                "-go", $goal,
                "-sfn", $saveFolder,
                "-algo", "FedALA",
                "-data", $dataset.Name,
                "-ncl", [string]$dataset.NumClasses,
                "-m", "CNN",
                "-gr", "50",
                "-nc", "20",
                "-jr", "1.0",
                "-t", "1",
                "-pv", "0",
                "-eg", "1",
                "-lbs", "10",
                "-lr", "0.005",
                "-ls", "1",
                "-et", "1.0",
                "-s", "80",
                "-p", "2",
                "-dev", "cuda",
                "-did", "0",
                "--seed", [string]$seed,
                "--ld_mode", "score",
                "--ld_alpha", "0.5",
                "--ld_beta", "0.3",
                "--ld_gamma", "0.2",
                "--ld_use_speed", [string]$useSpeed,
                "--ld_use_link", [string]$useLink,
                "--ld_use_stale", [string]$useStale,
                "--ld_tau", $tauText,
                "--ld_v_max", "120.0",
                "--ld_k_max", "5.0",
                "--ld_verbose", "0",
                "--comm_base_cost", "1.0",
                "--comm_penalty_scale", "5.0"
            )

            $displayArguments = foreach ($argument in $pythonArgs) {
                if ($argument -match "\s") {
                    '"{0}"' -f $argument
                }
                else {
                    $argument
                }
            }
            $commandText = "python {0}" -f ($displayArguments -join " ")

            $record = [PSCustomObject]@{
                run_index = $runIndex
                status = "RUNNING"
                dataset = $dataset.Name
                variant = $variant
                seed = $seed
                tau = $tauText
                ld_use_speed = $useSpeed
                ld_use_link = $useLink
                ld_use_stale = $useStale
                goal = $goal
                save_folder = $saveFolder
                console_log = $consoleLogPath
                command = $commandText
            }

            $manifest += $record
            $manifest | Export-Csv -LiteralPath $manifestPath -NoTypeInformation -Encoding UTF8

            Write-Host ""
            Write-Host ("=" * 76)
            Write-Host (
                "[{0}/{1}] Dataset={2}, Variant={3}, Seed={4}, Tau={5}" -f
                $runIndex, $totalRuns, $dataset.Name, $variant, $seed, $tauText
            )
            Write-Host $commandText
            Write-Host ("=" * 76)

            & python -u @pythonArgs 2>&1 | Tee-Object -FilePath $consoleLogPath
            $exitCode = $LASTEXITCODE

            if ($exitCode -ne 0) {
                $record.status = "FAILED_$exitCode"
                $manifest | Export-Csv -LiteralPath $manifestPath -NoTypeInformation -Encoding UTF8
                throw (
                    "Experiment failed. Dataset={0}, Variant={1}, Seed={2}. Console log: {3}" -f
                    $dataset.Name, $variant, $seed, $consoleLogPath
                )
            }

            $record.status = "PASS"
            $manifest | Export-Csv -LiteralPath $manifestPath -NoTypeInformation -Encoding UTF8
        }
    }
}

Write-Host ""
Write-Host "All 30 matched-ablation experiments completed."
Write-Host ("Result root : {0}" -f $runRoot)
Write-Host ("Manifest    : {0}" -f $manifestPath)
