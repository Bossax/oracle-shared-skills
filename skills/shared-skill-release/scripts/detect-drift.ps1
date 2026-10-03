<#
.SYNOPSIS
  Detects drift in assets not covered by junctions: .agents\skills\ mirror,
  multi-client subagent definitions (.claude, .agents, .codex), and hooks.

.PARAMETER ProjectRoot
  Root of the project to check, e.g. C:\Users\sitth\OracleWorkspace\Arun_Creagy

.EXAMPLE
  .\detect-drift.ps1 -ProjectRoot "C:\Users\sitth\OracleWorkspace\Arun_Creagy"
#>
param(
    [Parameter(Mandatory = $true)][string]$ProjectRoot
)

$sharedRoot = if (Test-Path (Join-Path $ProjectRoot ".oracle-shared-skills")) {
    Join-Path $ProjectRoot ".oracle-shared-skills"
} else {
    $ProjectRoot
}
$sharedSkills  = Join-Path $sharedRoot "skills"
$sharedAgents  = Join-Path $sharedRoot "agents"

$projectAgentSkills = Join-Path $ProjectRoot ".agents\skills"
$projectClaudeAgents = Join-Path $ProjectRoot ".claude\agents"
$projectAgyAgents    = Join-Path $ProjectRoot ".agents\agents"
$projectCodexAgents  = Join-Path $ProjectRoot ".codex\agents"

# 1. Skills Drift
Write-Host "=== .agents\skills drift (vs oracle-shared-skills\skills) ==="
$foundSkillsDrift = $false
if (Test-Path $sharedSkills) {
    Get-ChildItem $sharedSkills -Directory | ForEach-Object {
        $name = $_.Name
        $localDir = Join-Path $projectAgentSkills $name
        if (-not (Test-Path $localDir)) {
            Write-Host "  MISSING: $name not in .agents\skills - run tools\sync-skills.ps1"
            $foundSkillsDrift = $true
            return
        }
        $sharedFiles = Get-ChildItem $_.FullName -Recurse -File | Where-Object { $_.FullName -notmatch '\\(\.venv|__pycache__)\\' }
        foreach ($sf in $sharedFiles) {
            $rel = $sf.FullName.Substring($_.FullName.Length)
            $lf = Join-Path $localDir $rel.TrimStart('\')
            if (-not (Test-Path $lf)) {
                Write-Host "  MISSING FILE: $name$rel - run tools\sync-skills.ps1"
                $foundSkillsDrift = $true
            } elseif ((Get-FileHash $sf.FullName -Algorithm SHA256).Hash -ne (Get-FileHash $lf -Algorithm SHA256).Hash) {
                Write-Host "  EDITED LOCALLY: $name$rel (apply fix in shared repo, then run tools\sync-skills.ps1)"
                $foundSkillsDrift = $true
            }
        }
    }
}
if (-not $foundSkillsDrift) { Write-Host "  none" }
Write-Host ""

# 2. Multi-Client Subagent Drift
Write-Host "=== Multi-Client Subagent Drift (vs oracle-shared-skills\agents) ==="
$foundAgentDrift = $false

# Check Claude Code & Antigravity (Markdown)
$expectedMdAgents = Get-ChildItem $sharedAgents -Filter "*.md" -ErrorAction SilentlyContinue
foreach ($agent in $expectedMdAgents) {
    # Check Claude
    $claudeTarget = Join-Path $projectClaudeAgents $agent.Name
    if (-not (Test-Path $claudeTarget)) {
        Write-Host "  MISSING IN CLAUDE: $($agent.Name) not in .claude\agents\"
        $foundAgentDrift = $true
    } elseif ((Get-FileHash $agent.FullName -Algorithm SHA256).Hash -ne (Get-FileHash $claudeTarget -Algorithm SHA256).Hash) {
        Write-Host "  CHANGED IN CLAUDE: $($agent.Name) differs from shared repo"
        $foundAgentDrift = $true
    }

    # Check Antigravity
    $agyTarget = Join-Path $projectAgyAgents $agent.Name
    if (-not (Test-Path $agyTarget)) {
        Write-Host "  MISSING IN ANTIGRAVITY: $($agent.Name) not in .agents\agents\"
        $foundAgentDrift = $true
    } elseif ((Get-FileHash $agent.FullName -Algorithm SHA256).Hash -ne (Get-FileHash $agyTarget -Algorithm SHA256).Hash) {
        Write-Host "  CHANGED IN ANTIGRAVITY: $($agent.Name) differs from shared repo"
        $foundAgentDrift = $true
    }
}

# Check Codex (TOML)
$expectedTomlAgents = Get-ChildItem $sharedAgents -Filter "*.toml" -ErrorAction SilentlyContinue
foreach ($agent in $expectedTomlAgents) {
    $codexTarget = Join-Path $projectCodexAgents $agent.Name
    if (-not (Test-Path $codexTarget)) {
        Write-Host "  MISSING IN CODEX: $($agent.Name) not in .codex\agents\"
        $foundAgentDrift = $true
    } elseif ((Get-FileHash $agent.FullName -Algorithm SHA256).Hash -ne (Get-FileHash $codexTarget -Algorithm SHA256).Hash) {
        Write-Host "  CHANGED IN CODEX: $($agent.Name) differs from shared repo"
        $foundAgentDrift = $true
    }
}

# Check for Retired Legacy Agents
$retiredList = @("th-argument-mapper.md", "th-verbalizer.md", "th-editorial-reviewer.md", "th-argument-mapper.toml", "th-verbalizer.toml", "th-editorial-reviewer.toml")
foreach ($retired in $retiredList) {
    @($projectClaudeAgents, $projectAgyAgents, $projectCodexAgents) | ForEach-Object {
        $p = Join-Path $_ $retired
        if (Test-Path $p) {
            Write-Host "  RETIRED AGENT STILL PRESENT: $p (run tools\sync-skills.ps1 to purge)"
            $foundAgentDrift = $true
        }
    }
}

if (-not $foundAgentDrift) { Write-Host "  none" }
Write-Host ""

# 3. Hook Drift
Write-Host "=== Hook drift (.claude\settings.local.json vs writing-th\setup\settings.local.hooks.json) ==="
$settingsPath  = Join-Path $ProjectRoot ".claude\settings.local.json"
$hooksTemplate = Join-Path $sharedRoot "skills\writing-th\setup\settings.local.hooks.json"
if ((Test-Path $settingsPath) -and (Test-Path $hooksTemplate)) {
    $localSettings = Get-Content $settingsPath -Raw | ConvertFrom-Json -AsHashtable
    $template      = Get-Content $hooksTemplate -Raw | ConvertFrom-Json -AsHashtable
    $localHooks    = if ($localSettings.ContainsKey("hooks")) { $localSettings["hooks"] } else { $null }
    $localJson     = if ($null -ne $localHooks) { $localHooks | ConvertTo-Json -Depth 10 -Compress } else { "" }
    $templateJson  = $template["hooks"] | ConvertTo-Json -Depth 10 -Compress
    if ($localJson -ne $templateJson) {
        Write-Host "  DIFFERENT: $settingsPath's hooks do not match the shared template."
    } else {
        Write-Host "  none - hooks match the shared template"
    }
} else {
    Write-Host "  could not compare (missing settings.local.json or template)"
}
