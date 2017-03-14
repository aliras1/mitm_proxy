'''import os
import socket, ssl
import codecs

s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
ssl_sock = ssl.wrap_socket(s,
                           cert_reqs=ssl.CERT_NONE,
                           ssl_version=ssl.PROTOCOL_TLSv1)
ssl_sock.connect(('87.229.70.46',443))
ssl_sock.send(b'GET / HTTP/1.1\nAccept: text/html, application/xhtml+xml, image/jxr, */*\nAccept-Language: en-US\nUser-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.10240\nAccept-Encoding: gzip, deflate\nHost: 444.hu\nConnection: Keep-Alive\nCookie: _ga=GA1.2.1096085497.1488938339; __gfp_64b=4woVT0MJLV0wywJuUntgu1ymKsd0lgT.n7FhZmQxZx3.27; bm_monthly_unique=true; bm_daily_unique=true; bm_sample_frequency=1; ibbid=BBID-01-01636215590318857; bm_last_load_status=NOT_BLOCKING\n\n')
data = codecs.escape_decode(ssl_sock.recv(18096))[0]
print((data))
#print(data)
ssl_sock.close()'''

import http.client
import http.client, urllib.parse


headers = {"Content-type": "application/x-www-form-urlencoded",
            "Accept": "text/plain"}
conn = http.client.HTTPConnection("127.0.0.1", 5555)
conn.request("GET", "/")
r1 = conn.getresponse()
print(r1.status, r1.reason)
print(r1.headers)
data1 = r1.read()  # This will return entire content.
print(data1)
