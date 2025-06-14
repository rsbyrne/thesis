import os

from riskengine import aliases, fbcode

if not __name__ == '__main__':
    raise Exception

with open(os.path.join(aliases.repodir, 'fbids.txt'), 'r') as f:
    fbids = f.read().split('\n')[:-1]
with open(os.path.join(aliases.repodir, '.credentials.txt'), 'r') as f:
    loginName, loginPass = f.read().strip('\n').split(' ')

# fbids = fbids[:1]
# fbids = fbids[-1:]
print(f"Pulling fbids {fbids}...")
fbcode.pull_datas(fbids, loginName, loginPass)
print("Pulled.")
