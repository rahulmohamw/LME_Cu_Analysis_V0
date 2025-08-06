#!/bin/bash
# run_analysis.sh - Linux/Mac automation script for GitHub repository
# Schedule with cron for daily execution at 7:30 PM

echo "========================================="
echo "LME Copper Analysis - Automated Run"
echo "Repository: lme-copper-analysis"
echo "Timestamp: $(date '+%Y-%m-%d %H:%M:%S')"
echo "========================================="

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Navigate to repository root
cd "$SCRIPT_DIR"

# Check if virtual environment exists and activate it (optional)
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

# Check if data directory exists
if [ ! -d "data" ]; then
    echo "Creating data directory..."
    mkdir -p data
fi

# Check if output directories exist
if [ ! -d "output" ]; then
    echo "Creating output directory..."
    mkdir -p output/backups
fi

# Check if CSV file exists
if [ ! -f "data/lme_copper_historical_data.csv" ]; then
    echo "ERROR: CSV file not found at data/lme_copper_historical_data.csv"
    echo "Please place your LME copper data file in the data/ directory"
    exit 1
fi

# Run the Python analysis
echo "Starting analysis..."
python3 copper_analysis.py

# Check if the analysis was successful
if [ $? -eq 0 ]; then
    echo "✓ Analysis completed successfully"
    
    # Display summary of results
    if [ -f "analysis_results.json" ]; then
        echo ""
        echo "Analysis Summary:"
        echo "-----------------"
        # Use Python to display a summary (optional)
        python3 -c "
import json
with open('analysis_results.json', 'r') as f:
    data = json.load(f)
    if 'pricing_strategy' in data and data['pricing_strategy']:
        best = data['pricing_strategy'][0]
        print(f\"Best Strategy: {best['name']}\")
        print(f\"Expected Performance: +{best['avg_performance_vs_monthly']:.2f}%\")
        print(f\"Success Rate: {best['success_rate']:.1f}%\")
    if 'metadata' in data:
        print(f\"Analysis Date: {data['metadata']['analysis_timestamp'][:10]}\")
        print(f\"Records Analyzed: {data['metadata']['total_records']}\")
" 2>/dev/null || echo "Could not display summary"
    fi
    
    echo ""
    echo "✓ Results saved to output/analysis_results.json"
    echo "✓ Dashboard updated: Open copper_dashboard.html to view"
    
    # Log success
    echo "$(date '+%Y-%m-%d %H:%M:%S') - Analysis completed successfully" >> analysis.log
else
    echo "✗ Analysis failed with error code $?"
    echo "$(date '+%Y-%m-%d %H:%M:%S') - Analysis failed with error code $?" >> analysis.log
    exit 1
fi

echo "========================================="

# Deactivate virtual environment if it was activated
if [ -d "venv" ]; then
    deactivate 2>/dev/null || true
fi

# Instructions for scheduling with cron:
# 1. Open crontab: crontab -e
# 2. Add this line for daily execution at 7:30 PM:
#    30 19 * * * /path/to/your/repo/run_analysis.sh >> /path/to/your/repo/analysis_cron.log 2>&1

---

@echo off
REM run_analysis.bat - Windows automation script for GitHub repository
REM Schedule with Task Scheduler for daily execution at 7:30 PM

echo =========================================
echo LME Copper Analysis - Automated Run
echo Repository: lme-copper-analysis
echo Timestamp: %date% %time%
echo =========================================

REM Navigate to the script directory (repository root)
cd /d "%~dp0"

REM Check if virtual environment exists and activate it (optional)
if exist "venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
)

REM Check if data directory exists
if not exist "data" (
    echo Creating data directory...
    mkdir data
)

REM Check if output directories exist
if not exist "output" (
    echo Creating output directory...
    mkdir output
    mkdir output\backups
)

REM Check if CSV file exists
if not exist "data\lme_copper_historical_data.csv" (
    echo ERROR: CSV file not found at data\lme_copper_historical_data.csv
    echo Please place your LME copper data file in the data\ directory
    exit /b 1
)

REM Run the Python analysis
echo Starting analysis...
python copper_analysis.py

REM Check if the analysis was successful
if %ERRORLEVEL% EQU 0 (
    echo Analysis completed successfully
    
    REM Display summary of results (optional)
    if exist "analysis_results.json" (
        echo.
        echo Analysis Summary:
        echo -----------------
        REM Use Python to display summary
        python -c "import json; data=json.load(open('analysis_results.json')); best=data['pricing_strategy'][0] if 'pricing_strategy' in data else None; print(f'Best Strategy: {best[\"name\"]}') if best else None; print(f'Expected Performance: +{best[\"avg_performance_vs_monthly\"]:.2f}%%') if best else None" 2>nul
    )
    
    echo.
    echo Results saved to output\analysis_results.json
    echo Dashboard updated: Open copper_dashboard.html to view
    
    REM Log success
    echo %date% %time% - Analysis completed successfully >> analysis.log
) else (
    echo Analysis failed with error code %ERRORLEVEL%
    echo %date% %time% - Analysis failed with error code %ERRORLEVEL% >> analysis.log
    exit /b %ERRORLEVEL%
)

echo =========================================

REM Deactivate virtual environment if it was activated
if exist "venv\Scripts\deactivate.bat" (
    call venv\Scripts\deactivate.bat 2>nul
)

REM Instructions for scheduling with Windows Task Scheduler:
REM 1. Open Task Scheduler
REM 2. Create Basic Task
REM 3. Name: "LME Copper Daily Analysis"
REM 4. Trigger: Daily at 7:30 PM
REM 5. Action: Start a program
REM 6. Program: cmd.exe
REM 7. Arguments: /c "C:\path\to\your\repo\run_analysis.bat"
REM 8. Start in: C:\path\to\your\repo