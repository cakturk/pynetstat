# -*- coding: utf-8 -*-
import socket as sk
import struct

PATH_TCP4_TBL = '/proc/net/tcp'
PATH_TCP6_TBL = '/proc/net/tcp6'
PATH_UDP4_TBL = '/proc/net/udp'
PATH_UDP6_TBL = '/proc/net/udp6'

# Socket states
ESTABLISHED         = 0x01
SYN_SENT            = 0x02
SYN_RECV            = 0x03
FIN_WAIT1           = 0x04
FIN_WAIT2           = 0x05
TIME_WAIT           = 0x06
CLOSE               = 0x07
CLOSE_WAIT          = 0x08
LAST_ACK            = 0x09
LISTEN              = 0x0a
CLOSING             = 0x0b

sk_states = [
	"UNKNOWN",
	"ESTABLISHED",
	"SYN_SENT",
	"SYN_RECV",
	"FIN_WAIT1",
	"FIN_WAIT2",
	"TIME_WAIT",
	"", # CLOSE
	"CLOSE_WAIT",
	"LAST_ACK",
	"LISTEN",
	"CLOSING",
]

def skstate_str(st):
    return sk_states[st]

class SockTabEntry(object):

    def __init__(self, local, rem, state, uid, inode):
        super(SockTabEntry, self).__init__()
        self.local_addr = local
        self.rem_addr = rem
        self.state = state
        self.uid = uid
        self.inode = inode

    def __str__(self):
        return '{0}, {1}, {2}, {3}'.format(self.local_addr, self.rem_addr, self.state, self.uid)
    __repr__ = __str__

IPV4_LEN = 4
IPV6_LEN = 16

class IP(object):

    def __init__(self, addr):
        super(IP, self).__init__()
        self.addr = addr

    def __str__(self):
        family = 0
        if len(self.addr) == IPV6_LEN:
            family = sk.AF_INET6
        elif len(self.addr) == IPV4_LEN:
            family = sk.AF_INET
        else:
            return "unrecognized family"
        s = struct.pack("B"*len(self.addr), *self.addr)
        return sk.inet_ntop(family, s)

    __repr__ = __str__


def uint32_be(i):
    return [(i >> 0) & 0xff,
            (i >> 8) & 0xff,
            (i >> 16) & 0xff,
            (i >> 24) & 0xff]

INET4_STRLEN = 8
INET6_STRLEN = 32

def ip4(i):
    addr = int(i, 16)
    return IP(uint32_be(addr))

def ip6(i):
    addr = []
    while i:
        p = i[:8]
        a = uint32_be(int(p, 16))
        addr.extend(a)
        i = i[8:]
    return IP(addr)

def ipbytes(i):
    if len(i) == INET4_STRLEN:
        return ip4(i)
    if len(i) == INET6_STRLEN:
        return ip6(i)
    return None

def parse_addr(s):
    f = s.split(':')
    if len(f) < 2:
        return
    port = int(f[1], 16)
    return (ipbytes(f[0]), port)

def parse_line(line):
    fields = line.split()
    if len(fields) < 12:
        return
    loc = parse_addr(fields[1])
    rem = parse_addr(fields[2])
    st = int(fields[3], 16)
    uid = int(fields[7])
    ino = fields[9]
    return SockTabEntry(loc, rem, st, uid, ino)

def do_netstat(f, accept):
    # discard header
    f.readline()
    socks = []
    for lin in f:
        ent = parse_line(lin)
        if accept and not accept(ent):
            continue
        socks.append(ent)
    return socks

def tcp_socks(accept=None):
    f = open(PATH_TCP4_TBL)
    return do_netstat(f, accept)

def tcp6_socks(accept=None):
    f = open(PATH_TCP6_TBL)
    return do_netstat(f, accept)

def udp_socks(accept=None):
    f = open(PATH_UDP4_TBL)
    return do_netstat(f, accept)

def udp6_socks(accept=None):
    f = open(PATH_UDP6_TBL)
    return do_netstat(f, accept)

services = {"udp":{}, "tcp":{}}
services_initialized = False

PATH_SERVICES = '/etc/services'

def read_services():
    f = open(PATH_SERVICES)
    for line in f:
        line = line.rstrip('\n')
        if line == "":
            continue
        i = line.find('#')
        if i >= 0:
            line = line[:i]
            if line == "":
                continue
        line = line.split()
        portnet = line[1].split('/')
        if len(portnet) < 2:
            continue
        port = int(portnet[0])
        net = portnet[1]
        if net not in services:
            services[net] = {}
        services[net][port] = line[0]

def service_name(proto, port):
    global services_initialized
    if not services_initialized:
        read_services()
        services_initialized = True
    try:
        return services[proto][port]
    except KeyError:
        pass
    return ''
