import os
import subprocess


def runAndGatherOutput(command):
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    print(stdout.decode('utf-8'))
    if stderr:
        print(stderr.decode('utf-8'))
    return stdout.decode('utf-8')

release_channel = os.environ.get('RELEASE_CHANNEL', 'development')

print(runAndGatherOutput('poetry install --with build --all-extras'))

print('Building web...')

commitHash = runAndGatherOutput('git rev-parse HEAD').strip()
upstream = runAndGatherOutput('git remote get-url origin').strip()

with open('version.ini', 'w') as versionFile:
    versionFile.write(f"""[DEFAULT]
version_number={commitHash}
release_channel={release_channel}
upstream={upstream}
""")

print(runAndGatherOutput('poetry run pygbag --ume_block 0 --template web.tmpl --build webMain.py'))
