#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"

if command -v pwsh >/dev/null 2>&1; then
  powershell_bin="$(command -v pwsh)"
elif command -v pwsh-preview >/dev/null 2>&1; then
  powershell_bin="$(command -v pwsh-preview)"
else
  printf '%s\n' \
    "未找到 PowerShell Core (pwsh 或 pwsh-preview)。" \
    "macOS 稳定版安装命令: brew install --cask powershell" \
    "macOS预览版安装命令: brew install --cask powershell@preview" \
    "安装后重新运行本命令。"
  exit 127
fi

exec "${powershell_bin}" -NoLogo -NoProfile \
  -File "${script_dir}/run_from_config.ps1" \
  "$@"
