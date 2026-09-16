# ===========================================
# Download GitHub Repo to Skillable Desktop
# ===========================================

# Set variables
$repository = $env:WORKSHOP_GITHUB_REPOSITORY
$branch = if ($env:WORKSHOP_GITHUB_BRANCH) { $env:WORKSHOP_GITHUB_BRANCH } else { "main" }
$targetPath = "C:\Users\LabUser\Desktop\foundry-iq-agent-ready-knowledge-main"
$tempZip = "$env:TEMP\repo.zip"

if ([string]::IsNullOrWhiteSpace($repository)) {
    throw "WORKSHOP_GITHUB_REPOSITORY is required in owner/repository format."
}

# Download as ZIP using GitHub API
$headers = @{
    Accept = "application/vnd.github+json"
}
if ($env:GITHUB_TOKEN) {
    $headers.Authorization = "Bearer $env:GITHUB_TOKEN"
}

$zipUrl = "https://api.github.com/repos/$repository/zipball/$branch"

Invoke-WebRequest -Uri $zipUrl -Headers $headers -OutFile $tempZip -UseBasicParsing

# Extract to temp location
$tempExtract = "$env:TEMP\extracted"
if (Test-Path $tempExtract) {
    Remove-Item $tempExtract -Recurse -Force
}
Expand-Archive -Path $tempZip -DestinationPath $tempExtract -Force

# Find the extracted folder and move to final location
$extractedFolder = Get-ChildItem $tempExtract -Directory | Select-Object -First 1

if (Test-Path $targetPath) {
    Remove-Item $targetPath -Recurse -Force
}
Move-Item $extractedFolder.FullName $targetPath -Force
