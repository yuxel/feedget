"""
Feedget service using Tornado web
Its simply serving RSS/Atom contents as JSONP data
"""
import tornado.httpserver
import tornado.ioloop
import tornado.web

import feedparser #ultimate feed parser
import simplejson 

class FeedgetService(tornado.web.RequestHandler):
    def get(self, url):
        #todo: cache this data
        data = feedparser.parse(url)

        items = []
        for entry in data['entries']:
            item = {}
            item["title"] = entry.title
            item["link"]  = entry.link
            item["summary"] = entry.summary

            items.append ( item )
        
        jsonpData = self.get_argument('jsoncallback')  + '(' + simplejson.dumps(items) + ')'
        #todo:unset
        self.write(jsonpData)

application = tornado.web.Application([
    (r"/(.*)", FeedgetService),
])

if __name__ == "__main__":
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(8888)
    tornado.ioloop.IOLoop.instance().start(),
