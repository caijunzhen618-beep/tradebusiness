param(
    [string]$OutputDirectory = ".\backups",
    [int]$KeepDays = 14
)

$ErrorActionPreference = "Stop"

New-Item -ItemType Directory -Force -Path $OutputDirectory | Out-Null
$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$backupPath = Join-Path $OutputDirectory "tradebusiness-$timestamp.sql"

Write-Host "Creating database backup: $backupPath"

# 密码由 Docker Compose 从环境变量注入到容器，不写入命令行或日志。
docker compose -f docker-compose.prod.yml exec -T mysql sh -c 'mysqldump --single-transaction --quick --routines --triggers -u root -p"$MYSQL_ROOT_PASSWORD" "$MYSQL_DATABASE"' | Out-File -FilePath $backupPath -Encoding utf8

if (-not (Test-Path $backupPath) -or (Get-Item $backupPath).Length -eq 0) {
    throw "Database backup was not created or is empty."
}

$cutoff = (Get-Date).AddDays(-$KeepDays)
Get-ChildItem -Path $OutputDirectory -Filter "tradebusiness-*.sql" -File |
    Where-Object { $_.LastWriteTime -lt $cutoff } |
    Remove-Item -Force

Write-Host "Database backup completed successfully."
