import http.client
from http.server import HTTPServer, BaseHTTPRequestHandler
import ssl
import socketserver
from cgi import parse_header, parse_multipart
from urllib.parse import parse_qs
import http.client, urllib.parse
import gzip
from urllib.parse import urlparse
import logging


logging.basicConfig(filename="log",
                        filemode='a',
                        format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                        datefmt='%H:%M:%S',
                        level=logging.DEBUG)
logger = logging.getLogger('http server log')


stop = 1


class MyHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        print('[*] GET', self.headers['Host'] + "/" + self.path)
        hs = {}
        for h in self.headers:
            #if str(h) != 'Accept-Encoding':
            hs[h] = self.headers[h]
        print("\t\tcookie: ", self.headers['Cookie'])
        print("\n")

        for i in range(10):
            try:
                conn = http.client.HTTPConnection(self.headers['Host'])
                conn.request("GET", self.path, headers=hs)  # TODO check if headers are working
                r1 = conn.getresponse()
                data1 = r1.read()

                self.send_response(r1.status)
                for h in r1.headers:
                    self.send_header(h, r1.headers[h])
                self.end_headers()
                self.wfile.write(data1)
                return
            except Exception as e:
                logger.error("while do_GET" + str(e))

    def parse_POST(self):
        try:
            ctype, pdict = parse_header(self.headers['content-type'])
            if ctype == 'multipart/form-data':
                postvars = parse_multipart(self.rfile, pdict)
            elif ctype == 'application/x-www-form-urlencoded':
                length = int(self.headers['content-length'])
                try:
                    self.params = self.rfile.read(length)
                    d = self.params.decode('ascii')
                    postvars = parse_qs(d)
                except Exception as e:
                    print(str(e))
                    postvars = {}
            else:
                postvars = {}
            return postvars

        except Exception as e:
            logger.error("Error while parsing post variables")

    def do_POST(self):
        try:
            print("[*] POST " + self.headers['Host'] + " " + self.path)
            tmp = self.parse_POST()
            postvars = {}

            print("\t\tcookie: ", self.headers['Cookie'])
            for v in tmp:
                postvars[v] = tmp[v][0]

            print("\t\tPOST variables:")
            for v in postvars:
                print("\t\t\t", v, ": ", postvars[v])
            print("\n")
            hs = {}
            for h in self.headers:
                hs[h] = self.headers[h]
            conn = http.client.HTTPConnection(self.headers['Host'])
            conn.request("POST", self.path, self.params, self.headers)  # TODO check if headers are working
            r1 = conn.getresponse()

            data1 = r1.read()  # This will return entire content.

            self.send_response(r1.status)
            for h in r1.headers:
                self.send_header(h, r1.headers[h])
            self.end_headers()
            self.wfile.write(data1)
        except Exception as e:
            logger.error("in do_POST: " + str(e))

    def log_message(self, format, *args):
        return


class ForkingHTTPServer(socketserver.ThreadingMixIn, HTTPServer):
    def finish_request(self, request, client_address):
        request.settimeout(30)
        HTTPServer.finish_request(self, request, client_address)


def start_server(host_ip):
    global stop
    while stop:
        try:
            print("[*] HTTP server running...")
            httpd = ForkingHTTPServer((host_ip, 8080), MyHandler)
            httpd.serve_forever()  # serve_forever
        except Exception as e:
            print(str(e))
        finally:
            httpd.socket.close()
            httpd.server_close()
            print("[*] HTTP server stopped")