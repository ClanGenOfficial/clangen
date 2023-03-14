Move-Item -Path ./* -Destination oldfiles/ -Exclude Downloads,oldfiles -Force
Move-Item -Path ./Downloads/windows/Clangen/* ./ -Force
Remove-Item -Path ./Downloads -Recurse -Force
Remove-Item -Path ./oldfiles -Recurse -Force
& ./Clangen.exe