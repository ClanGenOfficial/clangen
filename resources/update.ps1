if ($args[0] -ne "internal") {
    Write-Output "This script is only for internal use, by our auto-updater. Exiting..."
    exit
}

Write-Output "Waiting for clangen to close..."
$clangen = Get-Process clangen -ErrorAction SilentlyContinue
if ($clangen) {
    $clangen.WaitForExit()
}
Write-Output "Clangen closed, continuing..."


Write-Output "Moving update files to the correct location..."


# move to ../

Set-Location ../

# delete old files
Write-Output "Deleting old files..."
Remove-Item -Recurse -Force 