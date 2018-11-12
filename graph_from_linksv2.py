# -*- coding: utf-8 -*-
"""
A scraping script that:
    (1) Generates a dictionary 'graph' of hyperlinks with directionality
    (2) Prints dead-end affiliate links

This software is for the analysis of affiliate links in a web page.  
Ideally, affiliates should link back to the site (undirected = directed graph)

Future -> Deep look (go X number of sites deep through site to look for 
                     longer paths)

Created on Fri Nov  9 21:06:07 2018

@author: vince
"""

#import libraries
import urllib.request
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from itertools import chain

#debug libraries
#import inspect

#specify URL
class WebSite():
    '''
    Get site and parse into important information
    '''
    
    def __init__(self, url):
        self.page = urllib.request.urlopen(url)
        self.html = BeautifulSoup(self.page, 'html.parser')
        self.links = {}
        
        print('Requested Website {}'.format(self.page.geturl()))
        
        self.get_links()
        

        
    def get_links(self):
        '''
        Get all links from the page
        '''
        hrefs = self.html.find_all('a', href=True)
        
        #Pull the URL's from find statement and store in a dictionary by domain.
        
        for line in hrefs:
            if 'http' in line['href']:
                temp_parse = parse_url(line['href'])
#                print('Temp Parse is ',temp_parse)
                self.add_links(temp_parse)

    def add_links(self, newlinks):
        '''
        Add new domains and links to self.links.
            Takes newlinks dictionary {domain: pathlist}
        '''
        for key in newlinks.keys():
            check_links = in_dict(self.links, newlinks, key)
            if not check_links[0]:
#                print('New enry being added: ', newlinks[key])
                self.links[key] = level_list([newlinks[key]])
                
            else:
                self.links[key] = self.links[key] + check_links[1]
            
#            print('Link List Is: ', self.links)

    
def level_list(listobj):
    '''
    Return a single nested list.  Some paths return as a list instead of a string.
    This ensures the dictionary object maintains level formatting during crawl.
    '''
    def nest_level(obj):
    
        # Not a list? So the nest level will always be 0:
        if type(obj) != list:
            return 0
    
        # Now we're dealing only with list objects:
    
        max_level = 0
        for item in obj:
            # Getting recursively the level for each item in the list,
            # then updating the max found level:
            max_level = max(max_level, nest_level(item))
    
        # Adding 1, because 'obj' is a list (here is the recursion magic):
        return max_level + 1
    
    #User itertools chain to get one less maximum nest level deep
    #A lot of computation for each item.  May want to skip if next level appropriate for add
    count = 0
    tempchain = listobj.copy()
    
    while count < nest_level(listobj) - 1:
        tempchain = list(chain(*tempchain))
        count += 1
    
    return tempchain

def parse_url(url):
    '''
    Implement urlparse and some filtering to get root domain and path from 
    passed URLs.
    
    Returns dictionary object. domain: path 
    '''
    parsed_url = urlparse(url)
    url_info = {}
    if 'www' in parsed_url.netloc:
        domain = parsed_url.netloc.split('www.')[1]
    else:
        domain = parsed_url.netloc
        
    url_info[domain] = parsed_url.path
    return url_info


def in_dict(*args):
    '''
    Quick true/false account of whether the value in dict2 is in the split
    list of values in dict1.  Assumes dict1.value(s) are comma-separated strings
    
    Returns a two item list: [Boolean True/False, [List of Items to Add]]
    '''
    
    dict1 = args[0]
    dict2 = args[1]
    key2match = args[2]
    newlinks = []
    bool_add = False
     
    if key2match in dict1.keys(): #Check if the key (domain) exists in master    
        testvec = dict1[key2match]
        bool_add = True
        
        if type(dict2[key2match]) == str:
            if dict2[key2match] not in testvec and check_path(dict2[key2match]) == False:
                newlinks.append(dict2[key2match])
        elif type(dict2[key2match]) == list:
            for path in dict2[key2match]: #Iterate through all paths    
                if path not in testvec and check_path(path) == False:
                    newlinks.append(path)
                
#    print('in_dict returning: ',[bool_add, newlinks])
    return [bool_add, newlinks]


def check_path(path):
    '''
    Check whether path is a page link or artifact (gif, png, jpg, jpeg)
    '''
    art_list = ['jpg', 'jpeg', 'png', 'gif', 'pdf']
    
    for art in art_list:
#        print('Is {} in path: {}'.format(art, path))
        if art in path:
            return True
    return False


def crawl_sites(links):
    '''
    Takes dictionary of domains and links (default) or list and generates
    unique list of pages to generate objects for.  Returns WebSite (should probably be page) objects
    of each page.
    '''
    def links_from_dict(dobj):
        '''
        Create absolute URL's from dictionary of unique domains and paths
        '''
        urllist = []
        for domain in dobj.keys():
            paths = dobj[domain]
            for path in paths:
                urlstring = 'http://www.' + domain + path
                urllist.append(urlstring)
                
        return urllist
    
    def create_web_objects(targetsites):
        hits = []
        for target in targetsites: 
            try: #May not be able to create page objects
                hits.append(WebSite(target))
            except:
                continue
        
        return hits
    
    #Check whether a list of links that can be directly crawled or a dictionary
    #was sent
    print('Beginning Crawl...Assessing Crawl Input Object...')
    
    if type(links) == dict:
        print('sent a dictionary')
        targets = links_from_dict(links)
    elif type(links) == list:
        print('sent a list')
        targets = links
    else:
        print('sent: {} which I cannot use!'.format(type(links)))
    
    print('\nSearching Targets...\n')
    #Send links to WebSite object generator
    return create_web_objects(targets)

def main():
    site = 'https://www.lazulidesigns.com/'
    
    search_level = 3 #Define search depth from main site
    print('Program Started - Building linklist for {}'.format(site))
    mainsite = WebSite(site)
    
    print('links before: ', mainsite.links)
    
    search = 0
    
    while search < search_level: #Currently inefficient, will re-search old pages
        for page in crawl_sites(mainsite.links):
            mainsite.add_links(page.links)
            print('\nlinks after {}: \n{}'.format(page.page.geturl(), mainsite.links))
            
            print('\n We have reached search level: ', search+1)
            
        search += 1
        

    
if __name__ == '__main__':
    main()
