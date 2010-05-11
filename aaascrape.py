#!/usr/bin/env python
# encoding: utf-8
"""
aaascraper.py

Created by Bruce Sheplan on 2010-05-11.
Copyright (c) 2010 sheplan.com. All rights reserved.
"""

import urllib2
import re
import sys
import getopt
import json
from BeautifulSoup import BeautifulSoup

baseUrl = "http://comunicados.acueductospr.com"
schema = ""
quiet = 1

def main(argv):
  
  try:
    opts, args = getopt.getopt(argv, "tscqn:h", ["text", "sql", "create", "quiet"])
  except getopt.GetoptError:
    print "ERROR: Did not understand arguments\n"
    usage()
    sys.exit(2)
  
  output = "text"
  max_news = 5
  create = 0
  global quiet
  
  for opt, arg in opts:
    if opt in ("-t", "--text"):
      output = "text"
    elif opt in ("-s", "--sql"):
      # output = "sql"
      pass
    elif opt in ("-c", "--create"):
      # create = 1
      pass
    elif opt in ("-n"):
      max_news = int(arg)
    elif opt in ("-q", "--quiet"):
      # quiet = 1
      pass
    elif opt in ("-h"):
      usage()
      sys.exit(0)
  
  debug("Initializing...\n")
  
  allData = getAllData(max_news)
  text = ""
  
  # for dataItem in allData:
  #   text += str(dataItem)
  
  text = json.dumps(allData, sort_keys=True, indent=4)
  # print "Text:" + text
  
  if output == 'sql':
    if create == 1:
      print schema
    print sql.encode('ascii', 'xmlcharrefreplace')
  else:
    print text.encode('ascii', 'xmlcharrefreplace')

def debug(data):
  if int(quiet) == 0:
    print >> sys.stderr, data,

def getAllData(max_news):
  newsItems = getNewsList(max_news)
  result = ['news', newsItems]
  
  i = 1
  
  for newsItem in newsItems:
    percent = float(i)/len(newsItems)*100;
    
    debug("Getting news data [" + str(i) + "/" + str(len(newsItems)) + "] (" + str(percent) + "%)\r")
    i += 1
    # print("URL: " + newsItem['url'])
    newsItem['content'] = getNewsContent(newsItem['url'])
    
    # debug("News item: " + str(newsItem) + "\n")
      
  debug("\n")
  
  return result

def getNewsContent(url):
  debug("Getting News Content...\n")
  # debug("url: " + str(baseUrl))
  res = getPage(url)

  soup = BeautifulSoup(res)
  mainBody = soup.findAll(id='mainContent')[0]

  return str(mainBody)


def getNewsList(max_news):
  debug("Getting News List...\n")
  # debug("url: " + str(baseUrl))
  res = getPage(baseUrl + "/AAACommBlog/AAACommBlog.nsf/archivelist?openview")
  
  soup = BeautifulSoup(res)
  mainBody = soup.findAll(id='mainContent')[0]
  newsItems = mainBody.findAll('a', {'href' : re.compile("OpenDocument$")})
  index = 0
  newsList = []
  for newsItem in [(x.string, x['href']) for x in newsItems]:
    newsList.append({'title': newsItem[0], 'url': baseUrl + '/' + newsItem[1]})
    index += 1
    if max_news > 0:
      if index >= max_news:
        break
  
  return newsList

def getPage(url):
  userAgent = 'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.6; en-US; rv:1.9.2.3) Gecko/20100401 Firefox/3.6.3'
  headers = { 'User-Agent' : userAgent }
  
  req = urllib2.Request(url, '', headers)
  response = urllib2.urlopen(req)
  return response.read()

def usage():
  print "usage: " + sys.argv[0] + " [-s|--sql] [-t|--text] [-c|--create] [-n limit]\n"
  print "Options:"
  print "\t-c, --create:\tOutput schema"
  print "\t-s, --sql:\tOutput in SQL for piping to mysql"
  print "\t-t, --text:\tOutput in human readable"
  print "\t-q, --quiet:\tSuppress Output"
  print "\t-n limit:\tOutput from N news items only"
  print "\t-h:\t\tThis message"

if __name__ == '__main__':
  main(sys.argv[1:])