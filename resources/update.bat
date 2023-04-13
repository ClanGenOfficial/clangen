@echo off
set arg1=%1
set arg2=%2
shift
shift

set arg1=%arg1:"=%

timeout /t 5
rmdir /s /q %arg1%
robocopy /E ".\clangen_update" "%arg1%"
echo "" > "%arg1%\auto-update"
echo "%arg1%/Clangen.exe"
"%arg1%/Clangen.exe"