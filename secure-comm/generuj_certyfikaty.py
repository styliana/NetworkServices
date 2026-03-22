from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import hashes
from cryptography.x509.oid import NameOID
from cryptography import x509
import datetime

def generuj_certyfikat_klienta():
    print("Wczytywanie klucza i certyfikatu CA...")
    # Wczytanie CA
    with open("ca.crt", "rb") as f:
        ca_cert = x509.load_pem_x509_certificate(f.read())
    with open("ca.key", "rb") as f:
        ca_key = serialization.load_pem_private_key(f.read(), password=None)

    print("Generowanie klucza prywatnego dla klienta...")
    # Generowanie klucza klienta
    client_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    
    # Zapis klucza prywatnego do pliku client.key
    with open("client.key", "wb") as f:
        f.write(client_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        ))

    print("Tworzenie i podpisywanie certyfikatu klienta...")
    # Dane certyfikatu klienta
    subject = x509.Name([
        x509.NameAttribute(NameOID.COMMON_NAME, u"quic-client"),
    ])
    
    # Budowanie certyfikatu podpisanego przez CA
    cert = x509.CertificateBuilder().subject_name(
        subject
    ).issuer_name(
        ca_cert.subject
    ).public_key(
        client_key.public_key()
    ).serial_number(
        x509.random_serial_number()
    ).not_valid_before(
        datetime.datetime.utcnow()
    ).not_valid_after(
        # Ważny przez 365 dni
        datetime.datetime.utcnow() + datetime.timedelta(days=365)
    ).sign(ca_key, hashes.SHA256())

    # Zapis certyfikatu do pliku client.crt
    with open("client.crt", "wb") as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))
        
    print("Sukces! Pliki 'client.key' oraz 'client.crt' zostały pomyślnie wygenerowane w tym folderze.")

if __name__ == "__main__":
    try:
        generuj_certyfikat_klienta()
    except FileNotFoundError as e:
        print(f"Błąd: Nie znaleziono pliku {e.filename}. Upewnij się, że jesteś w folderze 'secure-comm', w którym znajdują się pliki ca.crt i ca.key.")
    except Exception as e:
        print(f"Wystąpił nieoczekiwany błąd: {e}")