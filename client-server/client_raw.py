# Zapisz jako: client_raw.py
import socket
import struct

def checksum(msg):
    # Ręczne liczenie sumy kontrolnej dla nagłówka IP
    s = 0
    for i in range(0, len(msg), 2):
        w = (msg[i] << 8) + (msg[i+1])
        s = s + w
    s = (s >> 16) + (s & 0xffff)
    s = ~s & 0xffff
    return s

def main():
    try:
        # IPPROTO_RAW oznacza, że sami dostarczamy nagłówek IP
        s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
    except PermissionError:
        print("Brak uprawnień CAP_NET_RAW!")
        return

    source_ip = '127.0.0.1'
    dest_ip = '127.0.0.1'

    # Dane do wysłania
    user_data = b'Siema serwer, tu klient w Pythonie!'

    # --- BUDOWANIE NAGŁÓWKA IP ---
    ip_ihl = 5
    ip_ver = 4
    ip_tos = 0
    ip_tot_len = 20 + 8 + len(user_data)
    ip_id = 54321
    ip_frag_off = 0
    ip_ttl = 255
    ip_proto = socket.IPPROTO_UDP
    ip_check = 0
    ip_saddr = socket.inet_aton(source_ip)
    ip_daddr = socket.inet_aton(dest_ip)
    ip_ihl_ver = (ip_ver << 4) + ip_ihl

    # Pakujemy nagłówek bez sumy kontrolnej
    ip_header = struct.pack('!BBHHHBBH4s4s', ip_ihl_ver, ip_tos, ip_tot_len, ip_id, ip_frag_off, ip_ttl, ip_proto, ip_check, ip_saddr, ip_daddr)
    
    # Liczymy sumę i pakujemy jeszcze raz
    ip_check = checksum(ip_header)
    ip_header = struct.pack('!BBHHHBBH4s4s', ip_ihl_ver, ip_tos, ip_tot_len, ip_id, ip_frag_off, ip_ttl, ip_proto, ip_check, ip_saddr, ip_daddr)

    # --- BUDOWANIE NAGŁÓWKA UDP ---
    udp_source = 6666
    udp_dest = 80
    udp_length = 8 + len(user_data)
    udp_check = 0 # W UDP suma kontrolna jest opcjonalna, wpisujemy 0

    udp_header = struct.pack('!HHHH', udp_source, udp_dest, udp_length, udp_check)

    # Sklejamy całość
    packet = ip_header + udp_header + user_data

    # Wysyłamy surowy pakiet
    s.sendto(packet, (dest_ip, 0))
    print("Surowy pakiet wysłany!")

if __name__ == "__main__":
    main()