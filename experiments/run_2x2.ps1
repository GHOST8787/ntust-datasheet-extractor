# V3 2x2 dual-agent experiment driver
# Cells:
#   1. Mistral medium + conservative critic
#   2. GPT-4o + strict critic
#   3. GPT-4o + conservative critic
# (Mistral + strict already done = 68.2%, not re-running)

$ErrorActionPreference = 'Continue'
Set-Location 'C:\Users\sunny\Desktop\2025_NTUST\20260508_期末作業'

$cells = @(
    @{ backend = 'azure_mistral'; mode = 'conservative'; log = 'v3_run_mistral_conservative.log' },
    @{ backend = 'azure_gpt4o';   mode = 'strict';       log = 'v3_run_gpt4o_strict.log' },
    @{ backend = 'azure_gpt4o';   mode = 'conservative'; log = 'v3_run_gpt4o_conservative.log' }
)

$total = $cells.Count
$idx = 0
foreach ($cell in $cells) {
    $idx++
    $env:BACKEND = $cell.backend
    $env:CRITIC_PROMPT_MODE = $cell.mode
    Write-Output ('[{0}/{1}] Running: BACKEND={2}, CRITIC_PROMPT_MODE={3}' -f $idx, $total, $cell.backend, $cell.mode)
    python -u main.py *> $cell.log
    Write-Output ('[{0}/{1}] Done. Log: {2}' -f $idx, $total, $cell.log)
}

Write-Output 'All 3 cells finished.'
