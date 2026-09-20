# AquesTalk1（棒読みちゃん同梱DLL）で音声記号列をWAVに合成する。
#
# なぜPowerShellか: 同梱の AquesTalk.dll は 32bit 専用で、本体の Python は
# 64bit のため ctypes から直接呼べない。SysWOW64 の PowerShell は 32bit
# プロセスなので、追加インストールなしに 32bit の橋渡しができる。
#
# 呼び出しは必ず 32bit 側で行うこと:
#   C:\Windows\SysWOW64\WindowsPowerShell\v1.0\powershell.exe -NoProfile
#       -ExecutionPolicy Bypass -File scripts\aquestalk1.ps1
#       -Dll <...\AquesTalk\imd1\AquesTalk.dll> -TextFile <utf8.txt> -Out <out.wav>
#
# テキストは引数ではなくファイルで渡す。引数経由だとコンソールのコードページ次第で
# カタカナが化け、DLLが合成に失敗する（移行時に実際に踏んだ）。
param(
    [Parameter(Mandatory = $true)][string]$Dll,
    [Parameter(Mandatory = $true)][string]$TextFile,
    [Parameter(Mandatory = $true)][string]$Out,
    [int]$Speed = 100
)

$ErrorActionPreference = 'Stop'

if ([Environment]::Is64BitProcess) {
    Write-Output "ERR 64bitプロセスで実行されています。SysWOW64のpowershell.exeを使ってください"
    exit 1
}

$src = @"
using System;
using System.Runtime.InteropServices;
public static class Aq {
  [DllImport("AquesTalk.dll", CallingConvention = CallingConvention.StdCall)]
  public static extern IntPtr AquesTalk_Synthe(byte[] koe, int iSpeed, out int pSize);
  [DllImport("AquesTalk.dll", CallingConvention = CallingConvention.StdCall)]
  public static extern void AquesTalk_FreeWave(IntPtr wav);
  [DllImport("kernel32.dll", CharSet = CharSet.Unicode, SetLastError = true)]
  public static extern bool SetDllDirectory(string path);
}
"@
Add-Type -TypeDefinition $src

# DllImport はファイル名しか持たないので、探索パスを声ごとのフォルダへ向ける
[void][Aq]::SetDllDirectory((Split-Path -Parent $Dll))

# AquesTalk1 の音声記号列は Shift_JIS(CP932) のヌル終端
$text  = [IO.File]::ReadAllText($TextFile, [Text.Encoding]::UTF8).Trim()
$bytes = [Text.Encoding]::GetEncoding(932).GetBytes($text) + [byte]0

$size = 0
$p = [Aq]::AquesTalk_Synthe($bytes, $Speed, [ref]$size)
if ($p -eq [IntPtr]::Zero) {
    # このときの $size はエラーコード（101:音声記号列が長すぎる 105:未定義記号 等）
    Write-Output "ERR AquesTalk_Synthe失敗 code=$size"
    exit 1
}

$buf = New-Object byte[] $size
[Runtime.InteropServices.Marshal]::Copy($p, $buf, 0, $size)
[Aq]::AquesTalk_FreeWave($p)
[IO.File]::WriteAllBytes($Out, $buf)
Write-Output "OK bytes=$size"
