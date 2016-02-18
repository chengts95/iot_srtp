import tornado.web
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.websocket
import json
import redis
import os
import app_global
from traitlets.config.application import catch_config_error


cl = []

class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("index.html")



class WebSocketHandler(tornado.websocket.WebSocketHandler):

    def check_origin(self, origin):
        return True

    def on_message(self, message):
        print("message received " + message)
        response_to_send={}
        try:

            taggroup=message

            tags=[taggroup+'.TS',taggroup+'.NAME',taggroup+'.GY',taggroup+'.DY',taggroup+'.MB']
            for a in tags:
                response_to_send[a]={}
                response_to_send[a]["value"]=app_global.redisClient.get(a).decode()
        except IOError:
            response_to_send["error"]="500"
        self.write_message(json.dumps(response_to_send))

    def open(self):
        if self not in cl:
            cl.append(self)
            #self.write_message(u"Connected")
            app_global.clients_monitor_count += 1
            print("Rh WS open " + str(len(cl)) + " Total Client: ", str(app_global.clients_monitor_count))

    def on_close(self):
        if self in cl:
            cl.remove(self)
            app_global.clients_monitor_count -= 1
            print("Rh WS close " + str(len(cl)) + " Total Client: ", str(app_global.clients_monitor_count))



class ApiHandler(tornado.web.RequestHandler):

    @tornado.web.asynchronous
    def get(self, *args):

        uid = self.get_argument("id")
        value = self.get_argument("value")
        name=uid+"."+value
        payload = app_global.redisClient.get(name)
        if payload is not None:
            data = {"id": id, "value" : payload.decode()}
        else:
            data={"error":name + " not found"}
        self.write(data)
        self.finish()



    @tornado.web.asynchronous
    def post(self):
        pass

class realtimeHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self, *args):
        taggroup=self.get_argument("tag")

        title=u'在线监测'

        groupname=app_global.redisClient.get(taggroup+".NAME").decode()
        tagnames=self.get_tags(taggroup)

        self.render("test2.html",svg="/static/svg/bpr.min.svg",groupname=groupname,title=title,tagnames=tagnames)

    def get_tags(self,taggroup):

        tags=[taggroup+'.TS',taggroup+'.NAME',taggroup+'.GY',taggroup+'.DY',taggroup+'.MB']
        return  tags

class Application(tornado.web.Application):

    def __init__(self):
        handlers = [
             (r'/', realtimeHandler),
             (r'/ws', WebSocketHandler),
             (r'/api', ApiHandler),

        ]
        settings = dict(
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
        )

        tornado.web.Application.__init__(self, handlers, **settings)


if __name__ == '__main__':
#    app.listen(8888)
#    ioloop.IOLoop.instance().start()

    app = Application()
    server = tornado.httpserver.HTTPServer(app)
    server.listen(8000)
    tornado.ioloop.IOLoop.instance().start()
