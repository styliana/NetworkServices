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


        
''' 
Troszenke dokumentacji

Zapis !BBHHHBBH4s4s to tzw. łańcuch formatujący (format string) używany przez moduł struct w języku Python.
Służy on dokładnie do zbudowania nagłówka IPv4. Ponieważ korzystasz z gniazd surowych, 
musisz przetłumaczyć zwykłe liczby (np. długość pakietu, wersję IP) na ciąg surowych bitów i bajtów, 
które zrozumie karta sieciowa. Do tego właśnie służy ten dziwny ciąg znaków – mówi on Pythonowi, 
ile miejsca w pamięci ma zająć każda kolejna wartość.

Oto co oznacza każdy pojedynczy znak w tym kodzie:
! (Wykrzyknik) – Oznacza tzw. Network byte order (big-endian). 
Informuje Pythona: "Zapisz te bajty w kolejności standardowej dla protokołów sieciowych, 
a nie w kolejności domyślnej dla procesora mojego komputera".

B – Oznacza 1 bajt (małą liczbę całkowitą).
H – Oznacza 2 bajty (nieco większą liczbę całkowitą).
4s – Oznacza ciąg dokładnie 4 bajtów (ang. string o długości 4).

Jak to się mapuje na konkretne pola nagłówka IP w Twoim kodzie struct.pack(...)?

B (1 bajt): Wersja IP i długość nagłówka (ip_ihl_ver).
B (1 bajt): Typ usługi (ip_tos).
H (2 bajty): Całkowita długość pakietu (ip_tot_len).
H (2 bajty): Identyfikator pakietu (ip_id).
H (2 bajty): Flagi i przesunięcie fragmentacji (ip_frag_off).
B (1 bajt): Time to Live, czyli "czas życia" pakietu (ip_ttl).
B (1 bajt): Numer protokołu warstwy wyższej, u Ciebie UDP (ip_proto).
H (2 bajty): Suma kontrolna nagłówka (ip_check).
4s (4 bajty): Źródłowy adres IP (ip_saddr). Zwykły adres IPv4 składa się dokładnie z 4 liczb oddzielonych kropkami (np. 127.0.0.1), więc zajmuje w pamięci 4 bajty.
4s (4 bajty): Docelowy adres IP (ip_daddr).
'''