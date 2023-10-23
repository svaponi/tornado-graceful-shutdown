import asyncio
import json
import logging
import signal
import threading
import time

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web

logger = logging.getLogger()

_port = 8888
_should_stop = False
_request_counter = 0
_request_counter_lock = threading.Lock()


class BaseHandler(tornado.web.RequestHandler):

    def prepare(self):
        with _request_counter_lock:
            global _request_counter
            _request_counter += 1
        if _should_stop:
            self.send_error(410, reason="no more requests")

    def on_finish(self):
        with _request_counter_lock:
            global _request_counter
            _request_counter -= 1


class RootHandler(BaseHandler):

    def get(self):
        self.finish(f"<a target='_blank' href='/blocking'>/blocking<a><br/>"
                    f"<a target='_blank' href='/async'>/async<a>")


class BlockingHandler(BaseHandler):

    def get(self):
        name = type(self).__name__
        delay = int(self.get_argument("delay", "5"))
        for i in range(delay):
            logger.info(f"{name} is sleeping {i}/{delay} ...")
            time.sleep(1)
        logger.info(f"{name} is done")
        self.finish(json.dumps(dict(delay=delay, name=name)))


class AsyncHandler(BaseHandler):

    async def get(self):
        name = type(self).__name__
        delay = int(self.get_argument("delay", "5"))
        for i in range(delay):
            logger.info(f"{name} is sleeping {i}/{delay} ...")
            await asyncio.sleep(1)
        logger.info(f"{name} is done")
        self.set_status(200)
        await self.finish(json.dumps(dict(delay=delay, name=name)))


def start_server():
    urls = [
        (r'/', RootHandler),
        (r'/blocking', BlockingHandler),
        (r'/async', AsyncHandler),
    ]
    application = tornado.web.Application(urls)
    http_server = tornado.httpserver.HTTPServer(application, no_keep_alive=True)
    http_server.listen(_port)
    ioloop = tornado.ioloop.IOLoop.instance()

    def on_signal(sig, frame):
        global _should_stop
        http_server.stop()  # no more requests are accepted (only if no_keep_alive=True)
        _should_stop = True
        logger.info("Stopping server (no more requests) ...")

    def stop_if_necessary():
        global _should_stop
        if _should_stop:
            if _request_counter:
                logger.info(f"Waiting for {_request_counter} pending request(s)")
            else:
                ioloop.stop()

    # every second checks if server should stop
    tornado.ioloop.PeriodicCallback(stop_if_necessary, 1000).start()
    signal.signal(signal.SIGTERM, on_signal)
    signal.signal(signal.SIGINT, on_signal)
    logging.info(f"Starting server on http://localhost:{_port}")
    ioloop.start()


if __name__ == '__main__':
    tornado.options.parse_command_line()
    start_server()
    logging.info("Server stopped")
