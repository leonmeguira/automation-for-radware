import os
import sys
import subprocess

user = sys.argv[2]
password = sys.argv[3]
pypi_mode = {
    'test': 'https://test.pypi.org/legacy/',
    'prod': 'https://upload.pypi.org/legacy/'
}

dst = pypi_mode[sys.argv[1]]
os.chdir(os.path.join(os.path.dirname(__file__), '..'))
packages = ['alteon-sdk', 'sdk', 'ansible']

for p in packages:
    files = os.listdir(os.path.join(p, 'dist'))
    for file in files:
        path = os.path.join(p, 'dist', file)
        cmd = list(['twine', 'upload', path, '--repository-url', dst, '--skip-existing', '-u', user, '-p', password,
                    '--verbose'])
        subprocess.call(cmd, stderr=subprocess.STDOUT)
