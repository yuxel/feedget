"""
Feedget service using Tornado web
Its simply serving RSS/Atom contents as JSONP data
"""
import tornado.httpserver
import tornado.httpclient
import tornado.ioloop
import tornado.web

import feedparser #ultimate feed parser
import simplejson 
import time
import os

class FeedgetService(tornado.web.RequestHandler):
    
    def parseFeed(self, feedContent):
            
        if feedContent == None:
            raise Exception('1', "Not valid Feed" ) 

        
        fetchedData = feedparser.parse(feedContent)
        if fetchedData.bozo == 1:
            raise Exception('2', fetchedData.bozo ) 

        items = []
        for entry in fetchedData['entries']:
            #todo: atom feed support
            item = {}
            item["title"] = entry.title
            item["link"]  = entry.link
            item["summary"] = entry.summary
            item["updated"] = int(time.mktime(entry.updated_parsed))

            items.append ( item )
    
        return items

    @tornado.web.asynchronous
    def get(self, url):
        print ("request for " + url)
        # JavaScript callback method
        self.callbackMethod = "feedget.parser" 
        http = tornado.httpclient.AsyncHTTPClient()
        http.fetch(url, callback=self.async_callback(self.printData))

    def printData(self, response):
        try :
            parsedFeed = self.parseFeed(response.body)
            jsonDump = simplejson.dumps(parsedFeed);
        except Exception, error:
            print error
            output = {}
            output["error"] = {};
            output["error"]["code"] = error[0];
            output["error"]["message"] = error[1]
            jsonDump = simplejson.dumps(output)

        jsonpData = self.callbackMethod  + '( ' + jsonDump + ')'
        self.write(jsonpData)
            
        # thanks haldun for this fix
        self.finish()

#set static path for assets
settings = {
    "static_path": os.path.join(os.path.dirname(__file__), "static"),
}

application = tornado.web.Application([
    (r"/jsonp/(.*)", FeedgetService),
], **settings)

if __name__ == "__main__":
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(8888)
    tornado.ioloop.IOLoop.instance().start(),
