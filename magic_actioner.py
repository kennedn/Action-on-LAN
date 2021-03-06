#!/usr/bin/python3

import socket
import struct
from sys import argv
import subprocess as shell

# action to perform on valid WOL packet
action = "echo I'm a WOL packet!"
# Set this to a mac in format "00:11:22:33:44:55" if you wan't to override auto detection
mac_address = None
# port to look on for magic packets
port = 9

if len(argv) > 1:
    action = ' '.join(argv[1:])


# Try to derive mac address from default route, will work on linux.
if mac_address is None:
    try:
        p = shell.Popen(["ip", "route", "list", "0/0"], stdout=shell.PIPE)
        device = shell.check_output(["grep", "-v", "tun"], stdin=p.stdout).split()[4].decode()
        file = open("/sys/class/net/{}/address".format(device), "r")
        mac_address = file.read()
        file.close()
        print("Starting monitoring on {} with HWAddr {}".format(device, mac_address))
    except Exception:
        print("Couldn't detect mac address!")
        exit(1)

mac_address = mac_address.replace(':', '').rstrip()

# creating a rawSocket for communications
# PF_SOCKET (packet interface), SOCK_RAW (Raw socket) - htons (protocol) 0x0003 = All data with eth header
with socket.socket(socket.PF_PACKET, socket.SOCK_RAW, socket.htons(0x0003)) as rawSocket:
    while True:

        # read first packet in stream from recvfrom method, [0] to extract from tuple
        packet = rawSocket.recvfrom(2048)[0]

        eth_header = struct.unpack("!6s6s2s", packet[:14])  # dest_mac | source_mac | type
        # Remove eth header as we are done with it
        packet = packet[14:]

        # Data is processed the same no matter the packet type,
        # So set true if we are a WOL packet UDP or ETH
        valid_packet = False
        # If we are an eth frame, all that is left is the data to process.
        if eth_header[2] == b'\x08\x42':
            valid_packet = True
        # If instead we are a broadcast ipv4 packet, we need to do some more checks and processing
        # Before we can be certain this is a WOL packet
        elif eth_header[0] == b'\xff' * 6 and eth_header[2] == b'\x08\x00':
            # Header consists of:
            # version/header_length | type | total_length |
            # identifier | flags/frag_offset | time_to_live |
            # protocol | header_checksum | source_address, dest_address
            ip_header = struct.unpack("!ccHHHccH4s4s", packet[:20])

            # Remove ip header as we are done with it
            packet = packet[20:]

            # check if the packet protocol is UDP (0x11)
            if ip_header[6] == b'\x11':
                # Unpack the header portion of the UDP packet
                udp_header = struct.unpack("!HHHH", packet[:8])  # source_port | dest_port | length | checksum
                # Remove udp header as we are done with it
                packet = packet[8:]

                # if dest_port is 9 and size equals our expected packet size (102) + udp_header size
                if udp_header[1] == port and udp_header[2] == 102 + 8:
                    valid_packet = True

        if valid_packet:
            # Unpack data portion of the packet
            data = struct.unpack("!102s", packet)
            # Check the magic packet conforms to the expected format
            if data[0] == bytes.fromhex('ff' * 6 + mac_address * 16):
                shell.call(action.split())
