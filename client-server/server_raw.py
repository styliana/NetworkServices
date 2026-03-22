# Zapisz jako: server_raw.py
import socket

SERVER_PORT = 80  # Port poniżej 1024 wymaga specjalnych uprawnień
BUFFER_SIZE = 65535

def main():
    # Tworzymy surowe gniazdo UDP (odbiera całe pakiety)
    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_UDP)
    except PermissionError:
        print("Brak uprawnień! Użyj setcap na interpreterze Pythona.")
        return

    print(f"Serwer nasłuchuje na porcie {SERVER_PORT} (gniazda surowe)...")

    while True:
        # Odbieramy pakiet i adres nadawcy
        packet, addr = server_socket.recvfrom(BUFFER_SIZE)
        
        # W gnieździe surowym dostajemy cały pakiet IP.
        # Nagłówek IP ma zwykle 20 bajtów, nagłówek UDP ma 8 bajtów.
        # Wyciągamy dane (payload), które zaczynają się od 28 bajtu:
        ip_header = packet[0:20]
        udp_header = packet[20:28]
        payload = packet[28:]

        # Dekodujemy wiadomość
        try:
            message = payload.decode('utf-8')
            print(f"Otrzymano od {addr}: {message}")
            break # Kończymy po jednej wiadomości dla testu
        except UnicodeDecodeError:
            # Ignorujemy pakiety, które nie są naszym tekstem
            pass

if __name__ == "__main__":
    main()