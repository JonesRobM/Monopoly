# PowerShell script to run training with automatic timestamped logging
# Usage: .\train_with_logging.ps1 [-NumGames 1000] [-ResumeFrom 812]
# Examples:
#   .\train_with_logging.ps1 -NumGames 1000
#   .\train_with_logging.ps1 -NumGames 5000 -ResumeFrom 812

param(
    [int]$NumGames = 1000,
    [int]$ResumeFrom = 0
)

# Create logs directory if it doesn't exist
New-Item -ItemType Directory -Force -Path "logs" | Out-Null

# Generate timestamp for log filename
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"

# Build command and log filename
if ($ResumeFrom -eq 0) {
    Write-Host "Starting NEW training run for $NumGames games" -ForegroundColor Green
    $command = "python train.py --num_games $NumGames"
    $logFile = "logs/training_$timestamp.log"
} else {
    Write-Host "Resuming training from game $ResumeFrom for $NumGames games" -ForegroundColor Green
    $command = "python train.py --resume $ResumeFrom --num_games $NumGames"
    $logFile = "logs/training_resume_${ResumeFrom}_$timestamp.log"
}

Write-Host "Log file: $logFile" -ForegroundColor Cyan
Write-Host ""
Write-Host "Command: $command" -ForegroundColor Yellow
Write-Host ""
Write-Host "Press Ctrl+C to stop training and save checkpoint" -ForegroundColor Red
Write-Host "============================================================"
Write-Host ""

# Run training with logging (output to both console and file)
Invoke-Expression $command 2>&1 | Tee-Object -FilePath $logFile

Write-Host ""
Write-Host "============================================================" -ForegroundColor Green
Write-Host "Training complete! Log saved to: $logFile" -ForegroundColor Green
Write-Host ""
Write-Host "To analyze this run:" -ForegroundColor Cyan
Write-Host "  python analyze_training_logs.py $logFile" -ForegroundColor Yellow
Write-Host ""
