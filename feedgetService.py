"""
Feedget service using Tornado web
Its simply serving RSS/Atom contents as JSONP data
"""
import tornado.httpserver
import tornado.ioloop
import tornado.web

import feedparser #ultimate feed parser
import simplejson 
import time
import os

class FeedgetService(tornado.web.RequestHandler):
    
    def parseFeed(self, url):
        fetchedData = feedparser.parse(url)
        # check for errors or invalid feed
        if fetchedData.bozo == 1:
            raise Exception( '2', fetchedData.bozo_exception.getMessage() )

        else:
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

    def get(self, url):
        # JavaScript callback method
        callbackMethod = "feedget.parser" 

        try :
            parsedFeed = self.parseFeed(url)
            jsonDump = simplejson.dumps(parsedFeed);
        except Exception, error:
            output = {}
            output["error"] = {};
            output["error"]["code"] = error[0];
            output["error"]["message"] = error[1]
            jsonDump = simplejson.dumps(output)

        jsonpData = callbackMethod  + '( ' + jsonDump + ')'
        self.write(jsonpData)

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
