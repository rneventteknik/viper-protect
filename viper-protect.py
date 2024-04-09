import struct
import socket
import network
import wifinamepass

def connect_wifi():
    """Connect to wifi if its not already connected"""
    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        print("Connecting to network")
        sta_if.active(True)
        sta_if.connect(wifinamepass.wifi_name, wifinamepass.wifi_pass)
        while not sta_if.isconnected():
            pass
    else:
        print("Already connected")

    print("Network config", sta_if.ifconfig())

def listen_multicast():
    print("start to listen to multicast")

    mcast_group = mcast_group_from_universe(1)
    mcast_port = 5568

    # Get the adress in the corrcet format
    addr = socket.getaddrinfo(mcast_group, mcast_port)[0][-1]
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Set options
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    # Bind the socket
    sock.bind(addr)

    #Add socket to multicast group
    bin_addr = bytes(map(int, mcast_group.split(".")))
    mreq = struct.pack("4sl", bin_addr, 0)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    print("trying to recieve")
    packet = sock.recv(1024)
    print("recieved: ", len(packet), " bytes")

    print(get_source_name(packet))
    print(get_number_of_slots(packet), " values")

    print(get_dmx_values(packet))

    sock.close()

def get_source_name(packet: bytes) -> str:
    """Get the source name from the packet"""

    name_bytes = packet[44:108]

    return name_bytes.decode("utf-8")

def get_universe_number(packet: bytes) -> int:
    """Gets the universe as reported by the sacn packet"""

    return int.from_bytes(packet[113:115], "big")

def get_number_of_slots(packet: bytes) -> int:
    """Get the number of slots in the packet
    
    The number of slots is the same as the ammount of dmx valules sent in the packets. This is usually the whole universe.
    """
    return int.from_bytes(packet[123:125], "big")

def get_dmx_values(packet: bytes) -> list[int]:
    slots = get_number_of_slots(packet)

    slot_bytes = packet[125:125+ slots - 1]

    return list(slot_bytes)


def mcast_group_from_universe(universe: int) -> str:
    """Returns the correct multicast group adress based on the universe number"""

    data = universe.to_bytes(2, "big")

    return "239.255." + str(data[0]) + "." + str(data[1])

if __name__ == "__main__":
    connect_wifi()

    listen_multicast()
