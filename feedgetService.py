"""
Feedget service using Tornado web
Its simply serving RSS/Atom contents as JSONP data
"""
import tornado.httpserver
import tornado.httpclient
import tornado.ioloop
import tornado.web

import feedparser #ultimate feed parser
import time
import os


from tornado.options import define, options

define("port", default=8888, help="port for server", type=int)
define("callbackMethod", default="feedget.parser", help="callback method for JSONP requests", type=str)


class Application(tornado.web.Application):
  
    def __init__(self):
        handlers = [
            (r"/jsonp/(.*)", FeedgetService),
        ]

        settings = {
            "static_path": os.path.join(os.path.dirname(__file__), "static"),
        }

        tornado.web.Application.__init__(self, handlers, **settings)




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
        http = tornado.httpclient.AsyncHTTPClient()
        http.fetch(url, callback=self.async_callback(self.printData))

    def printData(self, response):
        try :
            output = self.parseFeed(response.body)
        except Exception, error:
            print error
            output = {}
            output["error"] = {};
            output["error"]["code"] = error[0];
            output["error"]["message"] = error[1]
        
        jsonDump = tornado.escape.json_encode(output)

        jsonpData = options.callbackMethod  + '( ' + jsonDump + ')'
        self.write(jsonpData)
            
        # thanks haldun for this fix
        self.finish()

if __name__ == "__main__":
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
