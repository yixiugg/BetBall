'''
Created on Mar 22, 2011

@author: a107818
'''
from HTMLParser import HTMLParser
import urllib   


class MyHtmlParser(HTMLParser):
    '''
    parse html
    '''


    def __init__(self):
        HTMLParser.__init__(self)
        self.flag=0;
        self.caption=0;
        self.v = "";
        self.result = [];
        self.date = "";
        self.pirorDate = "";
    

    def handle_starttag(self, tag, attrs):
        if tag == "td":
            for name,value in attrs:
                if name == "style" and value.index("background-color:") != -1:
                  
                    if(self.v != ""):
                        list = self.v.split(",")[0:18]
                        target = ""
                        for str in list :
                            target += str + ","
                            if str ==  '\xe7\x9b\x98\xe8\xb7\xaf':
                                d = self.date[5:7] +"-"+self.date[10:12]
                                if(self.flag == 0): 
                                    self.date = self.pirorDate
                                   
                                target += d+" "+ list[1]
                                break
                        self.result.append(target)
                        self.v = ""
                        
                    self.flag = 1;
        if tag == "caption":
            self.flag = 0
            self.caption = 1;
                       

    def handle_data(self,data):
        if self.flag == 1:
            if data.strip() != "":
                self.v += data + ","
        if self.caption == 1:
            self.pirorDate = data
            if self.date == "":
                self.date = self.pirorDate
    
    def handle_endtag(self,tag):
        if tag == "caption":
            self.caption = 0;
                
    def getListFromUrl(self,url):
        #sock = urllib.urlopen(url, proxies={'http' : 'http://proxy.statestr.com:80'}) 
        sock = urllib.urlopen(url) 
        htm = sock.read()    
        htm = unicode(htm, 'gb2312','ignore').encode('utf-8','ignore')
        self.feed(htm)
        return self.result;


if __name__ == '__main__':
    parser = MyHtmlParser()
    list = parser.getListFromUrl("http://odds.sports.sina.com.cn/odds/")
    for p in list:
        print p



        