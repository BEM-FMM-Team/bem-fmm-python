@echo off
set "S=%~dp0scripts\run.bat"
set "VBS=%~dp0run_hidden.vbs"

echo Set o = CreateObject("WScript.Shell") > "%VBS%"
echo o.Run Chr(34) ^& "%S%" ^& Chr(34), 0, False >> "%VBS%"

cscript //nologo "%VBS%"
del "%VBS%"
