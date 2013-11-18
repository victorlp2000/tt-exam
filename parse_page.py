#!/usr/bin/python
# -*- coding: utf8 -*-
#

from bs4 import BeautifulSoup
import json

##
# find link paths from the html page
#
def ParseNameLinks(html):
    soup = BeautifulSoup(html)
    table = soup.find("table", {"class":"listTable"})
    links = table.findAll("a", {"target":"_blank"})
    paths = []
    for link in links:
        paths.append(link['href'])
    return paths

##
# parse html page and return student info
#
def ParseStudentInfo(html):
    soup = BeautifulSoup(html)
    tables = soup.findAll("table")
    info = {}
    for table in tables:
        th = table.findAll("th")
        s1 = th[0].text.strip().encode('utf8')
        if s1 == "用户个人基本信息":
            index = 0;
            tds = table.findAll("td")
            while index < len(tds):
                name = tds[index].text.strip().encode('utf8')
                if name == "真实姓名":
                    info['name'] = tds[index+1].find("input")['value']
                    index += 1
                if name == "性别":
                    info['gender'] = tds[index+1].text.strip()
                    index += 1
                index += 1
    return info

##
# parse json text and return parent info
#
def ParseParentInfo(jstr):
    info = {}
    jobj = json.loads(jstr)
    info['father'] = jobj['father_name']
    info['mother'] = jobj['mother_name']
    return info

if __name__ == "__main__":
    import sys
    f = open(sys.argv[1])
    html = f.read()
    f.close()
    report = ParseStudentInfo(html)
    for k in report:
        print k, report[k]
