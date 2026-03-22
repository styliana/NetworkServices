# Zapisz jako: server_ipv6.py
import socket

# Adres IPv6 localhost i wysoki port (nie wymaga sudo)
HOST = '::1' 
PORT = 8080

def main():
    # AF_INET6 = wymuszamy IPv6
    # SOCK_STREAM = wymuszamy TCP (niezawodne połączenie)
    with socket.socket(socket.AF_INET6, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen(1) # Serwer czeka na maksymalnie 1 połączenie w kolejce
        print(f"Serwer TCP/IPv6 nasłuchuje na {HOST}:{PORT}...")
        
        # Akceptujemy przychodzące połączenie od klienta
        conn, addr = s.accept()
        with conn:
            print(f"Połączono z klientem o adresie: {addr}")
            while True:
                # Odbieramy dane (paczki po max 1024 bajty)
                data = conn.recv(1024)
                if not data:
                    break
                
                # Dekodujemy i wypisujemy na ekran
                print(f"Otrzymano wiadomość: {data.decode('utf-8')}")
                
                # Odsyłamy potwierdzenie do klienta
                conn.sendall(b"Serwer IPv6 mowi: Odebrano z sukcesem!")

if __name__ == "__main__":
    main()