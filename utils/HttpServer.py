import threading
from http.server import HTTPServer
from http.server import SimpleHTTPRequestHandler
import logging
import json

import wx

from mvp.presenter import PETPPresenter
from mvp.presenter.event.PETPEvent import PETPEvent


class HttpServer():

    def __init__(self, p: PETPPresenter):
        self.port = int(p.m.http_port)
        self.p = p

        global wxpython_view
        wxpython_view = p.v

    def start(self):
        httpd = HTTPServer(("", self.port), HttpRequestHandler)
        threading.Thread(target=httpd.serve_forever, daemon=True).start()
        logging.info(f"Http Server is serving at port {self.port}")


class HttpRequestHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_success_json(data={
            "available_post_endpoints": [
                {
                    "description": "Send a POST request to this endpoint to trigger a PETP event.",
                    "uri": "/petp",
                    "method": "POST",
                    "payload": {
                        "action": "execution",
                        "params": {"<data_key>": "<data_value>"}
                    }
                }
            ]
        })

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        payload = json.loads(self.rfile.read(content_length).decode('utf-8'))
        result = 'Not processed.'

        if self.path == '/petp':
            wx.PostEvent(wxpython_view, PETPEvent(PETPEvent.HTTP_CALLBACK, payload))
            result = 'Event sent to PETP.'

        # Send JSON response
        self.send_success_json(msg=result)

    def send_failure_response(self, code=500, data={}, msg="Failure"):
        self.send_json_response(code, data, msg)

    def send_success_json(self, code=200, data={}, msg="Success"):
        self.send_json_response(code, data, msg)

    def send_json_response(self, code=-1, data={}, msg=""):
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({
            "code": code,
            "data": data,
            "msg": msg
        }).encode('utf-8'))
