param(
    [string]$EnvFile = ".env.production"
)

$ErrorActionPreference = "Stop"
if (-not (Test-Path -LiteralPath $EnvFile)) {
    throw "Production env file not found: $EnvFile"
}

$values = @{}
Get-Content -LiteralPath $EnvFile | ForEach-Object {
    $line = $_.Trim()
    if ($line -and -not $line.StartsWith("#") -and $line.Contains("=")) {
        $key, $value = $line.Split("=", 2)
        $values[$key.Trim()] = $value.Trim().Trim('"')
    }
}

$required = @(
    "ENVIRONMENT", "SECRET_KEY", "JWT_SECRET_KEY", "CORS_ORIGINS",
    "MYSQL_ROOT_PASSWORD", "MYSQL_PASSWORD", "REDIS_PASSWORD",
    "SMTP_HOST", "SMTP_USER", "SMTP_PASSWORD", "SMTP_FROM"
)
foreach ($key in $required) {
    if (-not $values.ContainsKey($key) -or [string]::IsNullOrWhiteSpace($values[$key])) {
        throw "Missing required production variable: $key"
    }
}

if ($values["ENVIRONMENT"].ToLowerInvariant() -notin @("production", "prod")) {
    throw "ENVIRONMENT must be production or prod"
}
if ($values["CORS_ORIGINS"] -match "localhost|127\.0\.0\.1") {
    throw "CORS_ORIGINS must not contain localhost or 127.0.0.1"
}
foreach ($key in @("SECRET_KEY", "JWT_SECRET_KEY", "REDIS_PASSWORD")) {
    if ($values[$key].Length -lt 32 -or $values[$key] -match "replace-with|change-this") {
        throw "$key is too short or still contains a placeholder"
    }
}

Write-Host "Production environment verification passed: $EnvFile"
