import socket
import ssl

def main():
    # Konfiguracja kontekstu TLS dla klienta
    kontekst = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    
    # 1. Wczytanie CA do weryfikacji serwera (wymóg 3.5)
    kontekst.load_verify_locations(cafile="ca.crt")
    
    # 2. Wczytanie własnego certyfikatu dla serwera (mTLS - wymóg 4.0)
    kontekst.load_cert_chain(certfile="client.crt", keyfile="client.key")
    kontekst.verify_mode = ssl.CERT_REQUIRED
    
    # Dla testów na localhost omijamy sprawdzanie nazwy hosta
    kontekst.check_hostname = False

    # Zwykłe gniazdo TCP
    gniazdo_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # OPAKOWANIE gniazda w szyfrowany tunel TLS zanim się połączymy
    bezpieczne_gniazdo = kontekst.wrap_socket(gniazdo_tcp, server_hostname='127.0.0.1')
    
    print("Łączenie z serwerem TCP (TLS 1.3)...")
    try:
        bezpieczne_gniazdo.connect(('127.0.0.1', 8443))
        
        wiadomosc = "Siema! Tu stary, dobry klient TCP, ale z mTLS."
        print(f"Wysyłam: {wiadomosc}")
        bezpieczne_gniazdo.sendall(wiadomosc.encode('utf-8'))
        
        dane = bezpieczne_gniazdo.recv(1024)
        print(f"Odpowiedź: {dane.decode('utf-8')}")
        
    except ssl.SSLError as e:
        print(f"Błąd połączenia TLS: {e}")
    finally:
        bezpieczne_gniazdo.close()

if __name__ == "__main__":
    main()