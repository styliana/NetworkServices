# Zapisz jako: client_ipv6.py
import socket

# Adres serwera IPv6
HOST = '::1'
PORT = 8080

def main():
    # AF_INET6 dla IPv6, SOCK_STREAM dla TCP
    with socket.socket(socket.AF_INET6, socket.SOCK_STREAM) as s:
        print(f"Łączenie z serwerem {HOST}:{PORT}...")
        
        # W TCP musimy się najpierw połączyć (handshake)
        s.connect((HOST, PORT))
        print("Połączono!")
        
        # Wysyłamy wiadomość
        wiadomosc = "Siema, to leci po niezawodnym TCP i nowoczesnym IPv6!"
        s.sendall(wiadomosc.encode('utf-8'))
        
        # Czekamy na odpowiedź od serwera
        data = s.recv(1024)
        print(f"Odpowiedź z serwera: {data.decode('utf-8')}")

if __name__ == "__main__":
    main()