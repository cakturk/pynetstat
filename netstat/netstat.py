# -*- coding: utf-8 -*-

PATH_TCP_TBL = '/proc/net/tcp'
PATH_UDP_TBL = '/proc/net/udp'

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


def ipbytes(i):
    return [(i >> 0) & 0xff,
            (i >> 8) & 0xff,
            (i >> 16) & 0xff,
            (i >> 24) & 0xff]

def parse_addr(s):
    f = s.split(':')
    if len(f) < 2:
        return
    port = int(f[1], 16)
    addr = int(f[0], 16)
    return (ipbytes(addr), port)

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
    f = open(PATH_TCP_TBL)
    return do_netstat(f, accept)

def udp_socks(accept=None):
    f = open(PATH_UDP_TBL)
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
