import subprocess
import os

args = ['sdist', 'bdist_wheel', 'clean', '--all']
packages = ['alteon-sdk', 'sdk', 'ansible']

base = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

for p in packages:
    cmd = list()
    cmd.append('python')
    cmd.append(os.path.join(base, p, 'setup.py'))
    cmd.extend(args)
    subprocess.call(cmd, stderr=subprocess.STDOUT)



