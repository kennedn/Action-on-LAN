#!/usr/bin/python3

import socket
import struct
import subprocess as shell
import argparse

# Defaults (can be overridden via CLI)
DEFAULT_ACTION = "echo I'm a WOL packet!"
DEFAULT_MAC = "2c:f0:5d:56:40:43"
DEFAULT_WOL_PORT = 9
DEFAULT_HEALTH_PORT = 10

def parse_args():
    parser = argparse.ArgumentParser(
        description="Listen for WOL packets and optionally respond to UDP health checks."
    )
    parser.add_argument(
        "-m", "--mac",
        default=DEFAULT_MAC,
        help='MAC address to match, in the form "00:11:22:33:44:55".'
    )
    parser.add_argument(
        "-p", "--port",
        type=int,
        default=DEFAULT_WOL_PORT,
        help="UDP destination port to treat as WOL (default: 9)."
    )
    parser.add_argument(
        "--health-port",
        type=int,
        default=DEFAULT_HEALTH_PORT,
        help="UDP port to respond 'alive' on (default: 10)."
    )
    parser.add_argument(
        "command",
        nargs="*",
        help="Unix command to execute on receipt of a valid WOL packet."
    )
    return parser.parse_args()

def main():
    args = parse_args()

    # action to perform on valid WOL packet
    if args.command:
        action = " ".join(args.command)
    else:
        action = DEFAULT_ACTION

    # MAC address (CLI overrides default)
    mac_address = args.mac
    # port to look on for magic packets
    port = args.port
    # health-check UDP port
    health_port = args.health_port

    # Exit if no mac address
    if mac_address is None:
        print("No MAC address specified, exiting...")
        exit(1)

    mac_address = mac_address.replace(':', '').rstrip()
    mac_bytes = bytes.fromhex(mac_address)  # <--- bytes form for comparison
    print(f"Using MAC: {mac_address}")
    print(f"WOL UDP port: {port}")
    print(f"Health UDP port: {health_port}")
    print(f"Action on WOL: {action}")

    # creating a rawSocket for communications
    # PF_PACKET (packet interface), SOCK_RAW (Raw socket) - htons (protocol) 0x0003 = All data with eth header
    with socket.socket(socket.PF_PACKET, socket.SOCK_RAW, socket.htons(0x0003)) as rawSocket, \
         socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_sock:
        
        # Bind the UDP socket so the kernel treats the port as "open"
        udp_sock.bind(("", health_port))
        while True:
            # read first packet in stream from recvfrom method, [0] to extract from tuple
            packet = rawSocket.recvfrom(2048)[0]

            # dest_mac | source_mac | type
            eth_dest, eth_src, eth_type = struct.unpack("!6s6s2s", packet[:14])
            # Remove eth header as we are done with it
            packet = packet[14:]

            valid_packet = False

            # Pure Ethernet WOL frame (type 0x0842) 
            if eth_type == b'\x08\x42':
                valid_packet = True

            # IPv4 packet (type 0x0800), broadcast or unicast to our MAC
            elif eth_type == b'\x08\x00' and (eth_dest == b'\xff' * 6 or eth_dest == mac_bytes):
                # Header consists of:
                # version/header_length | type | total_length |
                # identifier | flags/frag_offset | time_to_live |
                # protocol | header_checksum | source_address, dest_address
                ip_header = struct.unpack("!ccHHHccH4s4s", packet[:20])
                packet = packet[20:]

                # check if the packet protocol is UDP (0x11)
                if ip_header[6] == b'\x11':
                    # source_port | dest_port | length | checksum
                    udp_src, udp_dst, udp_len, udp_checksum = struct.unpack("!HHHH", packet[:8])
                    packet = packet[8:]

                    # Health-check handling on health_port (simple "alive" response)
                    if udp_dst == health_port:
                        src_ip = socket.inet_ntoa(ip_header[8])  # source_address
                        try:
                            if packet.startswith(b"PING"):
                                src_ip = socket.inet_ntoa(ip_header[8])
                                udp_sock.sendto(b"PONG", (src_ip, udp_src))
                        except OSError:
                            # Ignore send errors and continue
                            pass

                    # if dest_port is WOL port and size equals our expected packet size (102) + udp_header size
                    if udp_dst == port and udp_len == 102 + 8:
                        valid_packet = True

            if valid_packet:
                # Unpack data portion of the packet
                data = struct.unpack("!102s", packet)
                # Check the magic packet conforms to the expected format
                if data[0] == bytes.fromhex('ff' * 6 + mac_address * 16):
                    shell.call(action.split())

if __name__ == "__main__":
    main()
