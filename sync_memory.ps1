# 双向同步记忆文件：本地 ↔ 备份（双项目）
# 规则：同名文件以较新版本覆盖较旧版本
# 用法：
#   .\sync_memory.ps1              → 同步全部项目
#   .\sync_memory.ps1 d--pyle      → 只同步 AI Agent 学习计划
#   .\sync_memory.ps1 e--pyle      → 只同步自动化测试进阶计划

param([string]$project = "all")

$projects = @(
    @{
        Name   = "d--pyle"
        Desc   = "AI Agent 学习计划"
        Local  = "$env:USERPROFILE\.claude\projects\d--pyle\memory"
        Backup = "d:\pyle\memory_backup"
    },
    @{
        Name   = "e--pyle"
        Desc   = "自动化测试进阶计划"
        Local  = "$env:USERPROFILE\.claude\projects\e--pyle\memory"
        Backup = "e:\pyle\memory_backup"
    }
)

function Sync-OneProject($proj) {
    Write-Host "`n=== $($proj.Desc) ($($proj.Name)) ===" -ForegroundColor Cyan
    Write-Host "  本地 : $($proj.Local)"
    Write-Host "  备份 : $($proj.Backup)"

    if (-not (Test-Path $proj.Backup)) {
        New-Item -ItemType Directory -Force -Path $proj.Backup | Out-Null
        Write-Host "  备份目录已创建" -ForegroundColor Green
    }

    $allFiles = @{}
    Get-ChildItem $proj.Local -ErrorAction SilentlyContinue | ForEach-Object {
        $allFiles[$_.Name] = @{ Local = $_; Backup = $null }
    }
    Get-ChildItem $proj.Backup -ErrorAction SilentlyContinue | ForEach-Object {
        if ($allFiles.ContainsKey($_.Name)) { $allFiles[$_.Name].Backup = $_ }
        else { $allFiles[$_.Name] = @{ Local = $null; Backup = $_ } }
    }

    $synced = 0
    foreach ($name in $allFiles.Keys) {
        $l = $allFiles[$name].Local
        $b = $allFiles[$name].Backup

        if (-not $l) {
            Copy-Item $b.FullName "$($proj.Local)\" -Force
            Write-Host "  + 本地 <- 备份 : $name" -ForegroundColor Green
            $synced++
        }
        elseif (-not $b) {
            Copy-Item $l.FullName "$($proj.Backup)\" -Force
            Write-Host "  + 本地 -> 备份 : $name" -ForegroundColor Green
            $synced++
        }
        elseif ($l.LastWriteTime -gt $b.LastWriteTime) {
            Copy-Item $l.FullName $b.FullName -Force
            Write-Host "  ^ 本地 -> 备份 : $name (本地较新)" -ForegroundColor Yellow
            $synced++
        }
        elseif ($b.LastWriteTime -gt $l.LastWriteTime) {
            Copy-Item $b.FullName $l.FullName -Force
            Write-Host "  v 本地 <- 备份 : $name (备份较新)" -ForegroundColor Yellow
            $synced++
        }
        else {
            Write-Host "    - 一致      : $name" -ForegroundColor DarkGray
        }
    }

    if ($synced -eq 0) {
        Write-Host "  两边已完全同步。" -ForegroundColor Cyan
    }
    else {
        Write-Host "  共同步 $synced 个文件。" -ForegroundColor Cyan
    }
}

foreach ($proj in $projects) {
    if ($project -eq "all" -or $proj.Name -eq $project) {
        Sync-OneProject $proj
    }
}

Write-Host ""
