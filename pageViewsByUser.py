from xml.dom import minidom
import urllib.request
import xml.etree.ElementTree as ET
import mwviews.api.pageviews as pv
import numpy as np
import datetime
import pickle


# print('{:%Y-%m-%dT%H:%M:%SZ}'.format(datetime.datetime.now()))
client = pv.PageviewsClient()
userContribs = []

yearStart = 2010
# yearEnd = 2012
yearEnd = int(str(datetime.datetime.now())[:4])
yearsList = range(yearStart, yearEnd+1) # also include the year now
nrYears = len(yearsList)

# ucend = '{:%Y-%m-%dT%H:%M:%SZ}'.format(datetime.datetime.now())

months = [1,7,12]

runPart = ['L', 'R']

if runPart[0] == 'R':
  # for y in [6]: #range(nrYears):
  for y in range(nrYears):
    for m in range(2):
      ucstart='%d-%02d-01T00:00:00Z' % (yearsList[y], months[m])
      ucend='%d-%02d-30T23:59:00Z' % (yearsList[y], months[m+1])
      # ucend='2017-03-01T00:00:00Z'
      username = 'mrazvan22'
      nrReqLimit = 500
      userContribsRequest = 'https://ro.wikipedia.org/w/api.php?action=query&list=usercontribs&ucuser=%s&uclimit=%d' \
      '&ucdir=newer&ucstart=%s&ucend=%s&format=json' % (username, nrReqLimit, ucstart, ucend)
      print(userContribsRequest)
      # print(asd)
      web = urllib.request.urlopen(userContribsRequest)
      xmlString = web.read()
      print('get_web', xmlString.decode('ascii'))
      # print(type(str(xmlString)))
      import json
      jsonDict = json.loads(xmlString.decode('ascii'))
      print('jsonDict', jsonDict)
      if 'query' in jsonDict.keys():
        userContribs += jsonDict['query']['usercontribs']
        assert len(jsonDict['query']['usercontribs']) < (nrReqLimit - 10)

  ds = dict(userContribs=userContribs)
  pickle.dump(ds, open('userContribs.npz', 'wb'), protocol=pickle.HIGHEST_PROTOCOL)
else:
  userContribs = pickle.load(open('userContribs.npz', 'rb'))['userContribs']

# print('userContribs', len(userContribs), userContribs)
# print(asda)
# print('pageTitles', [c['title'] for c in userContribs ])
pageTitles = [c['title'] for c in userContribs if 'minor' not in c.keys()]
# print('-------------\n\n\n\n')
# print('pageTitles', [c['title'] for c in userContribs ])
# print(adsa)

from itertools import groupby
# pageGroups = groupby(pageTitles)
# pageFreq = {}
unqPages = np.unique(pageTitles)
nrUnqPages = len(unqPages)
nrChangesByMeToEachPage = np.zeros(nrUnqPages)
for p in range(nrUnqPages):
  nrChangesByMeToEachPage[p] = len([x for x in pageTitles if x == unqPages[p]])

sortedByFreqOrd = np.argsort(nrChangesByMeToEachPage)[::-1]

# print(pageTitles)
# print(unqPages)
# print('pageFreq', freqPages)
print(unqPages[sortedByFreqOrd])
# print(asda)

articlesWithMostChangesByMe = unqPages[sortedByFreqOrd][:40]
articlesWithMostChangesByMe = ['_'.join(x.split(' ')) for x in articlesWithMostChangesByMe]


nrArticles = len(articlesWithMostChangesByMe)
print('nrArticles', nrArticles)
print('articlesChosen', articlesWithMostChangesByMe)
# print(ads)

startDate = '20170101' # 1st jan
endDate = None # defaults to today
granularity = 'monthly'

if runPart[1] == 'R':
  viewsRes = client.article_views('ro.wikipedia', articlesWithMostChangesByMe, access= 'all-access',
                                  agent='all-agents', granularity=granularity, start=startDate, end=endDate)

  ds = dict(viewsRes=viewsRes)
  pickle.dump(ds, open('viewsRes.npz', 'wb'), protocol=pickle.HIGHEST_PROTOCOL)
else:
  viewsRes = pickle.load(open('viewsRes.npz', 'rb'))['viewsRes']

np.random.seed(2)
print(viewsRes)
valListOfList = [list(v.values()) for v in viewsRes.values()]
print('viewsRes', viewsRes)
filteredList = [[x for x in l if x is not None] for l in valListOfList ]
print('valListOfList', valListOfList)
print('filteredList', filteredList)
print(np.sum([np.sum(l) for l in filteredList]))

nrMonths = 12
viewsMatAM = np.zeros((nrArticles, nrMonths), float)

for mStamp in viewsRes.keys():
  currMonth = mStamp.month-1
  for article in viewsRes[mStamp].keys():
    # print('article', article)
    # print(articlesChosen.index(article))
    artIndex = articlesWithMostChangesByMe.index(article)
    # print(articlesChosen[artIndex])
    if viewsRes[mStamp][article] is not None:
      viewsMatAM[artIndex,currMonth] += viewsRes[mStamp][article]


print('-------------------')
sortedByViewsind = np.argsort(np.sum(viewsMatAM,axis=1))[::-1]

for a in range(nrArticles ):
  print(articlesWithMostChangesByMe[sortedByViewsind[a]], np.sum(viewsMatAM[sortedByViewsind[a], :]))