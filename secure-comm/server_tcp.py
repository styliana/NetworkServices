import socket
import ssl

def main():
    # Konfiguracja kontekstu TLS dla serwera
    kontekst = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    
    # 1. Wczytanie certyfikatu serwera (wymóg na 3.0 / 3.5)
    kontekst.load_cert_chain(certfile="server.crt", keyfile="server.key")
    
    # 2. Wczytanie CA i wymuszenie certyfikatu od klienta (mTLS - wymóg na 4.0)
    kontekst.load_verify_locations(cafile="ca.crt")
    kontekst.verify_mode = ssl.CERT_REQUIRED

    # Standardowe gniazdo TCP
    gniazdo_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    gniazdo_tcp.bind(('127.0.0.1', 8443))
    gniazdo_tcp.listen(5)

    print("Serwer TCP/TLS nasłuchuje na 127.0.0.1:8443...")
    
    while True:
        nowe_gniazdo, adres = gniazdo_tcp.accept()
        # OPAKOWANIE zwykłego gniazda TCP w szyfrowany tunel TLS
        try:
            bezpieczne_gniazdo = kontekst.wrap_socket(nowe_gniazdo, server_side=True)
            print(f"Połączono bezpiecznie z: {adres}")
            
            dane = bezpieczne_gniazdo.recv(1024)
            print(f"Otrzymano po TCP: {dane.decode('utf-8')}")
            
            odpowiedz = "Serwer TCP z mTLS potwierdza odbiór!"
            bezpieczne_gniazdo.sendall(odpowiedz.encode('utf-8'))
            
        except ssl.SSLError as e:
            print(f"Błąd TLS (np. klient bez certyfikatu): {e}")
        finally:
            # Zawsze zamykamy bezpieczne gniazdo
            bezpieczne_gniazdo.close()

if __name__ == "__main__":
    main()