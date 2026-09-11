param(
    [string]$Godot = "$PSScriptRoot/../.tools/godot/Godot_v4.7.2-stable_win64_console.exe",
    [switch]$SkipTests
)
$ErrorActionPreference = 'Stop'
$repo = (Resolve-Path "$PSScriptRoot/..").Path
$project = Join-Path $repo 'godot'
if (-not (Test-Path -LiteralPath $Godot)) { throw 'Godot ausente. Consulte GODOT.md para instalar editor e templates.' }
New-Item -ItemType Directory -Force "$project/content", "$project/export/windows", "$project/export/web" | Out-Null
Copy-Item -Path "$repo/content/*" -Destination "$project/content" -Recurse -Force
function Invoke-Godot([string[]]$Arguments) {
    $result = & $Godot @Arguments 2>&1
    $code = $LASTEXITCODE
    $result | Out-Host
    if ($code -ne 0 -or ($result -match 'SCRIPT ERROR:|Parse Error:|ERROR:')) { throw 'Falha no Godot; exportação interrompida.' }
}
Invoke-Godot @('--headless', '--path', $project, '--editor', '--import')
if (-not $SkipTests) {
    foreach ($test in @('reference_test', 'combat_test', 'system_test')) {
        Invoke-Godot @('--headless', '--path', $project, '--script', "tests/$test.gd", '--quit-after', '600')
    }
}
Invoke-Godot @('--headless', '--path', $project, '--export-release', 'Windows Desktop')
Invoke-Godot @('--headless', '--path', $project, '--export-release', 'Web')
Get-ChildItem "$project/export/windows", "$project/export/web" -File | Select-Object Name, Length
