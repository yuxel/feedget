#!/usr/bin/python

"""
" Feedget service using Tornado web
" Its simply serving RSS/Atom contents as JSONP data
"""
import tornado.httpserver
import tornado.httpclient
import tornado.ioloop
import tornado.web

import feedparser #ultimate feed parser
import time
import os
import memcache
import md5

from tornado.options import define, options

define("port", default=8888, help="port for server", type=int)
define("callbackMethod", default="feedget.parser", help="callback method for JSONP requests", type=str)
define("memcacheHostPort", default="127.0.0.1:11211", help="memcache host:port", type=str)


class Application(tornado.web.Application):
  
    def __init__(self):
        handlers = [
            (r"/jsonp/(.*)", FeedgetService),
        ]

        settings = {
            "static_path": os.path.join(os.path.dirname(__file__), "static"),
            "cache_engine" : memcache.Client([options.memcacheHostPort], debug=0),
        }

        tornado.web.Application.__init__(self, handlers, **settings)


class FeedgetService(tornado.web.RequestHandler):

    @tornado.web.asynchronous
    def get(self, url):

        self.cacheEngine = self.settings["cache_engine"]
        self.cacheKey = md5.md5(url).hexdigest()
        data = self.getFromMemcache()

        """
        " if url cached serve from memcache
        " else fetch data
        """
        if data == None:
            http = tornado.httpclient.AsyncHTTPClient()
            http.fetch(url, callback=self.async_callback(self.printJSONP))
        else:
            self.write(data)
            self.finish()
        
   
    """
    " get data for cacheKey from memcache
    """
    def getFromMemcache(self):
        try:
            data = self.cacheEngine.get(self.cacheKey)
            return data
        except Exception, error:
            return None

    """
    " set data for cacheKey from memcache
    """
    def setToMemcache(self, data):
        try:
            self.cacheEngine.set(self.cacheKey, data)
            return True
        except:
            return False
  

    """
    " parse feed from feedContent
    """
    def parseFeed(self, feedContent):
        if feedContent == None:
            raise Exception('1', "Not valid Feed" ) 

        fetchedData = feedparser.parse(feedContent)
        if fetchedData.bozo == 1:
            raise Exception('2', "Malformatted feed" ) 


        items = []
        for entry in fetchedData['entries']:
            item = {}
            item["title"] = entry.title
            item["link"]  = entry.link
            item["description"] = None #will be popuplated below
            item["date"] = None #will be populated below


            
            try: #for rss feeds
                item["description"] = entry.description
            except: #for atom feeds
                item["description"] = entry.summary

            try: #for rss
                item["date"] = int(time.mktime(entry.date_parsed))
            except: #for atom
                item["date"] = int(time.mktime(entry.updated_parsed))

            items.append ( item )
    
        return items


    """
    " print data as JSONP
    """
    def printJSONP(self, response):
        success = False
        
        try :
            output = self.parseFeed(response.body)
            success = True
        except Exception, error:
            output = {}
            output["error"] = {};
            output["error"]["code"] = error[0];
            output["error"]["message"] = error[1]
        
        jsonDump = tornado.escape.json_encode(output)

        jsonpData = options.callbackMethod  + '( ' + jsonDump + ')'
        
        """
        " set data to memcache on success
        """
        if success == True:
            self.setToMemcache(jsonpData)

        self.write(jsonpData)
            
        # thanks haldun for this fix
        self.finish()

if __name__ == "__main__":
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
