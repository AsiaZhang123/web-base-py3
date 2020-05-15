from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop

from mobile_portal_py3 import app


def main():
    # http_server = HTTPServer(WSGIContainer(app))
    # http_server.listen(3298)
    # IOLoop.instance().start()
    app.run('0.0.0.0', port=3298)


if __name__ == '__main__':
    main()





