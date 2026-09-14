param(
    [string]$TemplatePath = "$PSScriptRoot\..\deploy\nginx\tradebusiness.conf.example"
)

$ErrorActionPreference = "Stop"
$content = Get-Content -LiteralPath $TemplatePath -Raw
$required = @(
    "listen 443 ssl",
    "return 301 https://",
    "ssl_certificate ",
    "ssl_certificate_key ",
    "Strict-Transport-Security",
    "proxy_pass http://tradebusiness_api",
    'try_files $uri $uri/ /index.html'
)

foreach ($item in $required) {
    if ($content -notmatch [regex]::Escape($item)) {
        throw "Nginx template is missing required directive: $item"
    }
}

Write-Host "Nginx template verification passed: $TemplatePath"
