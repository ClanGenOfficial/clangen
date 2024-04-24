import subprocess

def runAndGatherOutput(command):
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    return stdout.decode('utf-8')

commitHash = runAndGatherOutput('git rev-parse HEAD').strip()
branchName = runAndGatherOutput('git rev-parse --abbrev-ref HEAD').strip()
upstream = runAndGatherOutput('git remote get-url origin').strip()

with open('version.ini', 'w') as versionFile:
    versionFile.write(f"""[DEFAULT]
version_number={commitHash}
release_channel={branchName}
upstream={upstream}
""")

runAndGatherOutput('poetry run pygbag --ume_block 0 --template web.tmpl --build webMain.py')
