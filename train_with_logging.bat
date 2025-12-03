@echo off
REM Batch script to run training with automatic timestamped logging
REM Usage: train_with_logging.bat [num_games] [resume_from]
REM Examples:
REM   train_with_logging.bat 1000
REM   train_with_logging.bat 5000 812

setlocal enabledelayedexpansion

REM Create logs directory if it doesn't exist
if not exist logs mkdir logs

REM Generate timestamp for log filename
for /f "tokens=2-4 delims=/ " %%a in ('date /t') do (set mydate=%%c%%a%%b)
for /f "tokens=1-2 delims=/:" %%a in ('time /t') do (set mytime=%%a%%b)
set mytime=%mytime: =0%
set timestamp=%mydate%_%mytime%

REM Parse arguments
set NUM_GAMES=%1
if "%NUM_GAMES%"=="" set NUM_GAMES=1000

set RESUME_FROM=%2

REM Build command
if "%RESUME_FROM%"=="" (
    echo Starting NEW training run for %NUM_GAMES% games
    set COMMAND=python train.py --num_games %NUM_GAMES%
    set LOGFILE=logs\training_%timestamp%.log
) else (
    echo Resuming training from game %RESUME_FROM% for %NUM_GAMES% games
    set COMMAND=python train.py --resume %RESUME_FROM% --num_games %NUM_GAMES%
    set LOGFILE=logs\training_resume_%RESUME_FROM%_%timestamp%.log
)

echo Log file: %LOGFILE%
echo.
echo Command: %COMMAND%
echo.
echo Press Ctrl+C to stop training and save checkpoint
echo ============================================================
echo.

REM Run training with logging (output to both console and file)
%COMMAND% 2>&1 | python -c "import sys; [print(line, end='', flush=True) or open(r'%LOGFILE%', 'a', encoding='utf-8').write(line) for line in sys.stdin]"

echo.
echo ============================================================
echo Training complete! Log saved to: %LOGFILE%
echo.
echo To analyze this run:
echo   python analyze_training_logs.py %LOGFILE%
echo.

pause
