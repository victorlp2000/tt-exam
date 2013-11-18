#!/usr/bin/python
# -*- coding: utf8 -*-
#

import urllib
import cookielib, urllib2
import parse_page as PARSER

g_headers = {
    'Accept-Language':'en-US,en;q=0.8,zh-Hans-CN;q=0.5,zh-Hans;q=0.3',
    'User-Agent':'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; WOW64; Trident/6.0)',
    'Host':'stu.juren.com',
    'DNT':'1',
    'Connection':'Keep-Alive'
}

##
# send http request with url, headers, and body
# return received html and cookie
#
def GetHtml(url, headers, data):
    cj = cookielib.CookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    data = urllib.urlencode(data)
    headers.update(g_headers)
    request = urllib2.Request(url, data, headers)
    try:
        page = opener.open(request)
        html = page.read()
    except urllib2.HTTPError:
        print "http error:", url
        return None
    except urllib2.URLError:
        print "url error: ", url
        return None

    cookie = {}
    for ck in cj:
        cookie[ck.name] = ck.value
    return (html, cookie)

##
# extract cookie strings, return string like "name=value;..."
#
def GetCookie(cookie):
    cks = None
    for ck in cookie:
        if cks != None:
            cks += ";"
        else:
            cks = ""
        cks += ck + "=" + cookie[ck]
    return cks
 
##
# login to account, return authentication cookie string
#   
def Login(data):
    # goto home page
    url = "http://stu.juren.com/?action=eduAdmin.jingsai.login!login"
    headers = {
        'Accept':'text/html, application/xhtml+xml, */*'
    }
    (html, cookie) = GetHtml(url, headers, "")
    ck1 = GetCookie(cookie)

    headers = {
        'Accept':'text/html, application/xhtml+xml, */*',
        'Content-Type':'application/x-www-form-urlencoded',
        'Referer':url
    }
    if ck1 != None:
        headers['Cookie'] = ck1
    (html, cookie) = GetHtml(url, headers, data)
    ck2 = GetCookie(cookie)
    if ck2 != None:
        return ck2
    return ck1

##
# get specific exam page with exam id and page number
# return html source
#
def GetExamPage(cookie, examId, page):
    url = "http://stu.juren.com/?action=eduAdmin.jingsai.exam!listExamStudent"
    url += "&exam_id=" + str(examId)
    url += "&page=" + str(page)
    headers = {
        'Accept':'text/html, application/xhtml+xml, */*',
        'Referer':'http://stu.juren.com/index.php?action=eduAdmin.jingsai.exam!list',
        'Cookie':cookie}
    (html, cookie) = GetHtml(url, headers, "")
    return html

##
# get and return student info
#
def GetParentInfo(cookie, studentId):
    url = "http://stu.juren.com/?action=eduAdmin.jingsai.student!getParentInfo"
    headers = {
        'Accept':'text/html, application/xhtml+xml, */*',
        'Referer':'http://stu.juren.com/?action=eduAdmin.jingsai.student!showStudent&id=' + str(studentId),
        'Cookie':cookie}
    data = {
        'user_id':studentId}
    (html, cookie) = GetHtml(url, headers, data)
    info = PARSER.ParseParentInfo(html)
    return info

##
# get and return parent info
#
def GetStudentInfo(cookie, examId, studentId):
    url = "http://stu.juren.com/?action=eduAdmin.jingsai.student!showStudent&id=" + str(studentId)
    headers = {
        'Accept':'application/json, text/javascript, */*',
        'Referer':'http://stu.juren.com/?action=eduAdmin.jingsai.exam!listExamStudent&exam_id=' + str(examId),
        'Cookie':cookie}

    (html, cookie) = GetHtml(url, headers, "")
    info = PARSER.ParseStudentInfo(html)
    return info

##
# save text line to file
#
def appendToFile(line, append=False):
    mode = "a"
    if append is True:
        mode = "w"
    with open("tt.txt", mode) as myfile:
        myfile.write(line.encode("utf8") + '\n')
        myfile.close()

def Report(obj):
    line = '"' + obj['name'] + '","' + obj['gender'] + '","' + obj['father'] + '","' + obj['mother'] + '"'
    appendToFile(line)

def Main(username, password):
    data = {
        'frames':'yes',
        'admin_username':username,
        'admin_password':password,
        'admin_questionid':'0',
        'admin_answer':'',
        'submit':'提交'
    }
    examId = 187
    cookie = Login(data)
    appendToFile("name,gender,father,mother", True)
    for page in range(1, 172):
        print "page:", page
        html = GetExamPage(cookie, examId, page)
        links = PARSER.ParseNameLinks(html)
        for link in links:
            studentId = int(link[link.find("id=") + 3:])
            info = GetStudentInfo(cookie, examId, studentId)
            info.update(GetParentInfo(cookie, studentId))
            Report(info)

if __name__ == "__main__":
    import sys
    print len(sys.argv)
    if len(sys.argv) > 2:
        Main(sys.argv[1], sys.argv[2])
    else:
        print "missing username and password"

