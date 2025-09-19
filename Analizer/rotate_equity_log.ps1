# Equity Log Rotation Script - XAU 5-Minutes Terminal
# This script rotates the EquityLogClean.csv file daily at 7am
# It archives the current file with a date suffix for the 5-minute trading strategy
# MT4 will automatically create a new file when needed

param(
    [string]$LogPath = "C:\Users\maste\AppData\Roaming\MetaQuotes\Terminal\86A291B1D90FFC0E898CD5E9CF51C4F1\MQL4\Files\EquityLogClean.csv",
    [string]$ArchiveDir = "C:\Users\maste\OneDrive\Documentos\archived_logs\xau-5-minutes"
)

# Function to write log messages
function Write-Log {
    param([string]$Message)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logMessage = "[$timestamp] [XAU-5MIN] $Message"
    Write-Host $logMessage
    Add-Content -Path "$PSScriptRoot\rotation_5min.log" -Value $logMessage
}

try {
    Write-Log "Starting equity log rotation for XAU 5-minutes terminal..."
    
    # Create archive directory if it doesn't exist
    if (-not (Test-Path $ArchiveDir)) {
        New-Item -ItemType Directory -Path $ArchiveDir -Force
        Write-Log "Created archive directory: $ArchiveDir"
    }
    
    # Check if the log file exists
    if (-not (Test-Path $LogPath)) {
        Write-Log "Warning: Log file not found at $LogPath - nothing to rotate"
        Write-Log "Rotation completed (no file to rotate)"
        exit 0
    }
    
    # Get file info
    $fileInfo = Get-Item $LogPath
    $fileSize = [math]::Round($fileInfo.Length / 1MB, 2)
    Write-Log "Current log file size: $fileSize MB"
    
    # Only rotate if file is not empty
    if ($fileInfo.Length -eq 0) {
        Write-Log "Log file is empty, no rotation needed"
        exit 0
    }
    
    # Get yesterday's date for the archive filename (since we're rotating at 7am)
    $yesterday = (Get-Date).AddDays(-1).ToString("yyyy-MM-dd")
    $archiveFileName = "EquityLogClean_$yesterday.csv"
    $archivePath = Join-Path $ArchiveDir $archiveFileName
    
    # Check if archive file already exists and add counter if needed
    if (Test-Path $archivePath) {
        $counter = 1
        do {
            $archiveFileName = "EquityLogClean_$yesterday`_$counter.csv"
            $archivePath = Join-Path $ArchiveDir $archiveFileName
            $counter++
        } while (Test-Path $archivePath)
    }
    
    # Move the current log to archive (MT4 will recreate the file automatically)
    Move-Item -Path $LogPath -Destination $archivePath
    Write-Log "Archived log file to: $archivePath"
    Write-Log "MT4 will automatically create a new log file when needed"
    
    # Optional: Clean up old archives (keep last 30 days)
    $cutoffDate = (Get-Date).AddDays(-30)
    $deletedCount = 0
    Get-ChildItem -Path $ArchiveDir -Name "EquityLogClean_*.csv" | ForEach-Object {
        $fileName = $_
        if ($fileName -match "EquityLogClean_(\d{4}-\d{2}-\d{2})") {
            $fileDate = [DateTime]::ParseExact($matches[1], "yyyy-MM-dd", $null)
            if ($fileDate -lt $cutoffDate) {
                $fullPath = Join-Path $ArchiveDir $fileName
                Remove-Item -Path $fullPath -Force
                Write-Log "Deleted old archive: $fileName"
                $deletedCount++
            }
        }
    }
    
    if ($deletedCount -eq 0) {
        Write-Log "No old archives to clean up"
    } else {
        Write-Log "Cleaned up $deletedCount old archive files"
    }
    
    Write-Log "Equity log rotation completed successfully for XAU 5-minutes terminal"
    
} catch {
    Write-Log "ERROR: $($_.Exception.Message)"
    Write-Log "Stack trace: $($_.ScriptStackTrace)"
    exit 1
}