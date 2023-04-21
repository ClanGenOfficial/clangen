from PyInstaller import __main__ as pyi
import os
import shutil
import platform

directory = os.path.dirname(__file__)
if directory:
    os.chdir(directory)

print('Creating temporary files...')
os.makedirs('tmp', exist_ok=True)
with open('tmp/version.ini', 'w') as f:
    f.write(f"""
    [DEFAULT]
    version_number={os.environ.get('VERSION_NUMBER', '0.0.0')}
    release_channel={os.environ.get('RELEASE_CHANNEL', 'development')}
    upstream={os.environ.get('UPSTREAM', 'Thlumyn/clangen')}
    """)

isDev = os.environ.get('RELEASE_CHANNEL', 'development') == 'development'

if platform.system() == 'Windows':
    with open('tmp/datadir.bat', 'w') as f:
        f.write(fr"""
start "%LocalAppData%\ClanGen\ClanGen{'Beta' if isDev else ''}"
""")
elif platform.system() == 'Linux':
    with open('tmp/datadir.sh', 'w') as f:
        f.write(f"""#!/bin/sh
if [ -z "$XDG_DATA_HOME" ]; then
    xdg-open "$XDG_DATA_HOME/ClanGen/ClanGen{'Beta' if isDev else ''}"
else
    xdg-open "$HOME/.local/share/ClanGen/ClanGen{'Beta' if isDev else ''}"
fi
""")
        os.chmod('tmp/datadir.sh', 0o755)
elif platform.system() == 'Darwin':
    with open('tmp/datadir.sh', 'w') as f:
        f.write(f"""#!/bin/sh
open -R "~/Library/Application Support/ClanGen/ClanGen{'Beta' if isDev else ''}"
""")
        os.chmod('tmp/datadir.sh', 0o755)


print('Running PyInstaller...')

pyi.run(['Clangen.spec'])

print('Deleting temporary files...')

shutil.rmtree('tmp')
