# import os

# import fbcode

# repoPath = os.path.abspath(os.path.dirname(__file__))

# with open(os.path.join(repoPath, 'fbids.txt'), 'r') as f:
#     fbids = f.read().split('\n')[:-1]
# with open(os.path.join(repoPath, '.credentials.txt'), 'r') as f:
#     loginName, loginPass = f.read().strip('\n').split(' ')
# outExt = '.csv'
# dataMime = 'text/csv'
# masterURL = 'https://www.facebook.com/geoinsights-portal/downloads/?id='

# maxTries = 3

# for fbid in fbids:
#     outDir = os.path.join(repoPath, 'data', fbid)
#     dataURL = masterURL + fbid
#     tries = 0
#     while tries < maxTries:
#         try:
#             fbcode.pull_datas(dataURL, loginName, loginPass, outDir, dataMime, outExt)
#             break
#         except:
#             pass
#         tries += 1
#     if tries == maxTries:
#         print("Max tries reached downloading", fbid)