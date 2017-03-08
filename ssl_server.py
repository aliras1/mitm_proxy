from socketserver import TCPServer, ThreadingMixIn, StreamRequestHandler
import ssl
import http.client
import os
import socket
import codecs


'''class MySSL_TCPServer(TCPServer):
    def __init__(self,
                 server_address,
                 RequestHandlerClass,
                 certfile,
                 keyfile,
                 ssl_version=ssl.PROTOCOL_TLSv1,
                 bind_and_activate=True):
        TCPServer.__init__(self, server_address, RequestHandlerClass, bind_and_activate)
        self.allow_reuse_address = True
        self.certfile = certfile
        self.keyfile = keyfile
        self.ssl_version = ssl_version

    def get_request(self):
        newsocket, fromaddr = self.socket.accept()
        connstream = ssl.wrap_socket(newsocket,
                                 server_side=True,
                                 certfile = self.certfile,
                                 keyfile = self.keyfile,
                                 ssl_version = self.ssl_version)
        return connstream, fromaddr

class MySSL_ThreadingTCPServer(ThreadingMixIn, MySSL_TCPServer): pass

class testHandler(StreamRequestHandler):
    def handle(self):
        data = self.connection.recv(8096).decode('utf-8')
        while not data.endswith('\r\n\r\n'):
            data += self.connection.recv(8096).decode('utf-8')

        data = data.split('\r\n')
        GET = data[0].split(' ')[1]
        headers = {}
        for i in range(1, len(data)):
            line = data[i].split(': ')
            if len(line) >= 2:
                headers[line[0]] = line[1]

        print(GET)
        #print(headers)

        conn = http.client.HTTPSConnection("444.hu")
        conn.request("GET", GET)
        r1 = conn.getresponse()
        print(r1.status, r1.reason)
        data1 = r1.read()  # This will return entire content.
        #print(data1)

        self.wfile.write(data1)
        print("---- sent ----")
#test code
MySSL_ThreadingTCPServer(('192.168.0.23',4433),testHandler,"cert.pem","key.pem").serve_forever()'''


from http.server import HTTPServer, BaseHTTPRequestHandler
import ssl

class MyHandler(BaseHTTPRequestHandler):

    def do_GET(s):
        print('[**] ', s.path)

        conn = http.client.HTTPSConnection(s.headers['Host'])
        conn.request("GET", s.path)
        r1 = conn.getresponse()
        print(r1.status, r1.reason)
        data1 = r1.read()  # This will return entire content.
        #print(data1)
        s.wfile.write(data1)
        print("-------------")

httpd = HTTPServer(('192.168.0.23', 4433), MyHandler)
httpd.socket = ssl.wrap_socket (httpd.socket, certfile='cert.pem', keyfile='key.pem', server_side=True, cert_reqs=ssl.CERT_OPTIONAL)
httpd.serve_forever()