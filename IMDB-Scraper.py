#!/usr/bin/env python
# coding: utf-8

# In[308]:

import requests
import re
from bs4 import BeautifulSoup as bs
import pandas as pd
import numpy as np
import json


# ## IMDB Scrapper

with open('films_updated-52-last.json','r') as json_file:
    films = json.load(json_file)


# In[214]:


def checkNone(content):
    if content is not None:
        return content.text.strip()
    else:
        return None


# In[336]:


def webscraper(title):
    link = pref+title
    page = requests.get(link)
    soup = bs(page.text,'lxml')
    
    basics = soup.find('script',attrs={'type':'application/ld+json'})
    if basics is not None:
        basicInfo = json.loads(basics.text)
    else:
        basicInfo = {}
    
    meta = soup.find('div',attrs={'class':'titleReviewBar'})
    if meta is not None:
        metascore = checkNone(meta.find('a',attrs={'href':'criticreviews'}))
        metareviews = checkNone(meta.find('a',attrs={'href':'reviews'}))
        metacritic = checkNone(meta.find('a',attrs={'href':'externalreviews'}))
        basicInfo['meta']={'metaScore':metascore,'reviewCount':metareviews,'criticCount':metacritic}
    
    summary = soup.find('div',attrs={'class':'summary_text'})
    basicInfo['description'] = checkNone(summary)
    
    country = []
    language = []
    release = None
    
    df = soup.find('div',attrs={'id':'titleDetails'})
    if df is not None:
        divs = df.find_all('div',attrs={'class':'txt-block'})
        for div in divs:
            if div.find('h4') is not None and div.find('h4').text == 'Country:':
                couns = div.find_all('a')
                for coun in couns:
                    country.append(coun.text)
            if div.find('h4') is not None and div.find('h4').text == 'Language:':
                langs = div.find_all('a')
                for lang in langs:
                    language.append(lang.text)
            if div.find('h4') is not None and div.find('h4').text == 'Release Date:':
                release = re.sub('\n|Release Date:|See(.*)','',div.text)
                release = release.strip()
                
    basicInfo['language']=language
    basicInfo['country']=country
    basicInfo['releaseDate']=release
    
    link = pref+title+end1
    page = requests.get(link)
    soup = bs(page.text,'lxml')
    
    production = soup.find('h4', attrs={'id':'production'})
    if production is not None:
        com = production.find_next('ul').find_all('a')
        if 'creator' in basicInfo.keys():
            if type(basicInfo['creator'])==list:
                for i in range(len(com)):
                    basicInfo['creator'][-len(com)+i]['name']=com[i].text
            else:
                basicInfo['creator']['name']=com[0].text

    return basicInfo


# In[232]:


pref = 'https://imdb.com/title/'
end1 = '/companycredits'
end2 = '/releaseinfo'
titles = list(films.keys())


# In[319]:

for title in titles:
    basicInfo = webscraper(title)
    films[title].update(basicInfo)


# In[ ]:


with open('films_updated-52-last.json','w') as outfile:
    json.dump(films,outfile)





