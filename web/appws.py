import tornado.web
import tornado.httpserver
import tornado.ioloop
import tornado.options

import os

import realtime_u_gen_sheet_d3_ws_handler as gen
import realtime_u_rh_sheet_d3_ws_handler as rh
import realtime_u_ecs_sheet_d3_ws_handler as ecs

import RedisInfoMonitor_handler as redisinfo

import app_global as glb

class indexHandler(tornado.web.RequestHandler):

    def get(self):
        
        glb.clients_machine_ip.append(self.request.remote_ip)
        print('Client IP:', self.request.remote_ip)
        
        self.render("index.html")

class Application(tornado.web.Application):

    def __init__(self):
        handlers = [
            (r"/", indexHandler),
            
            (r"/realtime_u_gen_sheet_d3/", gen.realtimeHandler),
            (r"/genwebsocket", gen.WebSocketHandler),
           
            (r"/realtime_u_ecs_sheet_d3/", ecs.realtimeHandler),
            (r"/ecswebsocket", ecs.WebSocketHandler),
          
            (r"/realtime_u_rh_sheet_d3/", rh.realtimeHandler),
            (r"/rhwebsocket", rh.WebSocketHandler),
            
            (r"/redisinfomonitor/", redisinfo.RedisInfoHandler),
        ]

        settings = dict(
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
        )
        
        tornado.web.Application.__init__(self, handlers, **settings)

if __name__ == '__main__':
    tornado.options.parse_command_line()

    app = Application()
    server = tornado.httpserver.HTTPServer(app)
    server.listen(8000)

    mainLoop = tornado.ioloop.IOLoop.instance()
  
    scheduler_rh = tornado.ioloop.PeriodicCallback(rh.sendmsssage2client, 2000, io_loop=mainLoop)
    scheduler_ecs = tornado.ioloop.PeriodicCallback(ecs.sendmsssage2client, 2000, io_loop=mainLoop)
    scheduler_gen = tornado.ioloop.PeriodicCallback(gen.sendmsssage2client, 2000, io_loop=mainLoop)
 
    scheduler_rh.start()
    scheduler_ecs.start()
    scheduler_gen.start()
    
    print('Web Server start')
    mainLoop.start()
   
