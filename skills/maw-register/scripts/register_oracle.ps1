<#
.SYNOPSIS
    Registers a Windows Oracle repository into WSL MAW.

.PARAMETER Name
    Canonical Oracle name in MAW (e.g. aon, keth, jiu).

.PARAMETER RepoPath
    Windows path to the Oracle repository. Defaults to the current directory.

.PARAMETER Command
    Optional launch command override for maw.config.json (default uses "agy").

.PARAMETER Distro
    WSL distribution name. Defaults to Ubuntu.

.PARAMETER DryRun
    Prints the actions and WSL commands without making changes.
#>
param(
    [Parameter(Mandatory = $true)][string]$Name,
    [string]$RepoPath = (Get-Location).Path,
    [string]$Command = "",
    [string]$Distro = "Ubuntu",
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"

$resolvedRepo = (Resolve-Path $RepoPath).Path
if (-not (Test-Path (Join-Path $resolvedRepo "ψ"))) {
    throw "Missing 'ψ' directory in $resolvedRepo. Run /awaken first."
}

if ($resolvedRepo -match "^([A-Za-z]):(.*)$") {
    $drive = $Matches[1].ToLower()
    $rest = $Matches[2] -replace '\\', '/'
    $wslRepoPath = "/mnt/${drive}${rest}"
} else {
    throw "Could not translate Windows path to WSL path: $resolvedRepo"
}

$linkPath = "/home/sitth/Code/github.com/local/${Name}-oracle"

if ($DryRun) {
    Write-Host "[DryRun] Name:       $Name"
    Write-Host "[DryRun] Repo (Win): $resolvedRepo"
    Write-Host "[DryRun] Repo (WSL): $wslRepoPath"
    Write-Host "[DryRun] Symlink:    $linkPath -> $wslRepoPath"
    Write-Host "[DryRun] Command:    maw oracle register $Name"
    Write-Host "[DryRun] Config:     add agents.$Name = local in ~/.config/maw/maw.config.json"
    if ($Command) {
        Write-Host "[DryRun] Override:   add commands.$Name = $Command"
    }
    return
}

$cmdArg = $Command -replace "'", "'\''"
$bashScript = @'
set -euo pipefail
export PATH="$HOME/.bun/bin:$PATH"

NAME="__NAME__"
TARGET="__TARGET__"
LINK="__LINK__"
CUSTOM_CMD="__CMD__"

if ! command -v maw >/dev/null 2>&1; then
  echo "ERROR: maw not found in PATH ($PATH)" >&2
  exit 1
fi

mkdir -p "$(dirname "$LINK")"
if [ -L "$LINK" ]; then
  CURRENT="$(readlink "$LINK")"
  if [ "$CURRENT" != "$TARGET" ]; then
    echo "ERROR: $LINK already points to $CURRENT (expected $TARGET)" >&2
    exit 1
  fi
  echo "Symlink already matches: $LINK -> $TARGET"
elif [ -e "$LINK" ]; then
  echo "ERROR: $LINK exists and is a regular file or directory" >&2
  exit 1
else
  ln -s "$TARGET" "$LINK"
  echo "Created symlink: $LINK -> $TARGET"
fi

if maw oracle ls --json | grep -q "\"name\": \"$NAME\""; then
  echo "Oracle '$NAME' already in ~/.maw/oracles.json"
else
  maw oracle register "$NAME"
fi

CONFIG="$HOME/.config/maw/maw.config.json"
if [ -f "$CONFIG" ]; then
  CONFIG_PATH="$CONFIG" O_NAME="$NAME" O_CMD="$CUSTOM_CMD" bun -e '
    const fs = require("fs");
    const p = process.env.CONFIG_PATH;
    const cfg = JSON.parse(fs.readFileSync(p, "utf8"));
    cfg.agents = cfg.agents || {};
    if (!cfg.agents[process.env.O_NAME]) {
      cfg.agents[process.env.O_NAME] = cfg.node || "local";
    }
    if (process.env.O_CMD) {
      cfg.commands = cfg.commands || {};
      cfg.commands[process.env.O_NAME] = process.env.O_CMD;
    }
    fs.writeFileSync(p, JSON.stringify(cfg, null, 2) + "\n", "utf8");
  '
  echo "Updated $CONFIG"
fi

maw locate "$NAME"
'@

$bashScript = $bashScript.Replace("__NAME__", $Name).Replace("__TARGET__", $wslRepoPath).Replace("__LINK__", $linkPath).Replace("__CMD__", $cmdArg)
$encoded = [Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes($bashScript))
wsl -d $Distro -e bash -lc "echo '$encoded' | base64 -d | bash"
if ($LASTEXITCODE -ne 0) {
    throw "WSL registration failed with exit code $LASTEXITCODE"
}
