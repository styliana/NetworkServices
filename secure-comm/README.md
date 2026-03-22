# Projekt 2: Bezpieczna Komunikacja (TCP & QUIC z mTLS)

## 📌 O projekcie
Implementacja demonstruje zestawienie bezpiecznych, szyfrowanych kanałów komunikacji z wykorzystaniem zarówno klasycznego protokołu **TCP** (z biblioteką `ssl`), jak i nowoczesnego protokołu **QUIC** (z biblioteką `aioquic`). 

Kluczowym elementem projektu jest autorska infrastruktura PKI (Public Key Infrastructure) oraz wdrożenie **obustronnego uwierzytelniania (mTLS)**, gdzie zarówno serwer, jak i klient muszą wylegitymować się ważnym certyfikatem podpisanym przez zaufane Centrum Certyfikacji (CA).

---

## 🎯 Zrealizowane Wymagania (Kaskadowo)

1. Implementacja klienta i serwera TCP wykorzystujących szyfrowanie TLS.
2. Stworzenie własnego, lokalnego Centrum Certyfikacji (Root CA), wygenerowanie własnych kluczy i certyfikatów oraz użycie ich w kodzie.
3. Zastosowanie obustronnego uwierzytelniania (Mutual TLS). Serwer twardo weryfikuje certyfikat klienta przed nawiązaniem połączenia.
4. Implementacja klienta i serwera w oparciu o protokół QUIC (działający na warstwie UDP) z wbudowanym TLS 1.3 .

---

## 🔐 Infrastruktura PKI (Jak u nas działają certyfikaty?)

Aby zrealizować obustronne uwierzytelnianie bez ostrzeżeń o niezaufanych wystawcach, stworzono urząd certyfikacji (Root CA) i wydaliśmy certyfikaty dla podmiotów końcowych.

### Słowniczek plików:
* **`.key` (Klucz prywatny):** Ściśle tajny, asymetryczny klucz kryptograficzny (np. RSA 2048-bit). Służy do deszyfrowania danych oraz składania podpisów cyfrowych.
* **`.csr` (Certificate Signing Request):** Żądanie podpisania certyfikatu. Zawiera klucz publiczny podmiotu i jego dane (np. Common Name).
* **`.crt` (Certyfikat X.509):** Publiczny dokument poświadczający tożsamość, na którym urząd CA złożył swój podpis cyfrowy.

### Proces generowania w naszym projekcie (Krok po kroku):
1. **Inicjalizacja CA:** Wygenerowaliśmy klucz prywatny naszego urzędu (`ca.key`) i na jego podstawie utworzyliśmy publiczny, samopodpisany certyfikat root (`ca.crt`).
2. **Klucze podmiotów:** Klient i Serwer wygenerowali własne klucze prywatne (`client.key`, `server.key`).
3. **Wnioski CSR:** Na podstawie kluczy prywatnych wygenerowano żądania podpisania (`.csr`).
4. **Wystawienie certyfikatów:** Nasze CA (`ca.key`) podpisało kryptograficznie żądania, tworząc prawomocne certyfikaty końcowe (`client.crt`, `server.crt`).

Podczas łączenia się, obie strony wysyłają sobie pliki `.crt` i weryfikują je względem wczytanego wzoru zaufanego urzędu (`ca.crt`).

<img width="1867" height="522" alt="image" src="https://github.com/user-attachments/assets/7709e31a-bccd-4e8d-83e3-535095bde572" />


---

## Kluczowe elem. kodu.

Mechanika bezpieczeństwa (mTLS) opiera się na odpowiedniej konfiguracji kontekstu TLS w skryptach Pythona:

* `load_cert_chain(certfile="...", keyfile="...")`  
  *Ładuje do pamięci certyfikat podmiotu oraz jego klucz prywatny, aby podmiot mógł udowodnić swoją tożsamość drugiej stronie.*
* `load_verify_locations(cafile="ca.crt")`  
  *Wskazuje aplikacji, że ma ufać **tylko i wyłącznie** certyfikatom, które zostały cyfrowo podpisane przez ten konkretny plik Root CA.*
* `verify_mode = ssl.CERT_REQUIRED`  
  *Najważniejsza flaga dla oceny 4.0. Wymusza na serwerze twarde żądanie certyfikatu od klienta. Jeśli klient go nie wyśle (lub wyśle niepodpisany przez nasze CA), połączenie zostanie natychmiast zerwane.*
* `alpn_protocols=["projekt-quic-5.0"]` *(tylko QUIC)* *Application-Layer Protocol Negotiation. Zabezpiecza przed łączeniem się z naszym serwerem niekompatybilnych klientów, wymuszając z góry określony protokół aplikacyjny.*

---

## 🚀 Instrukcja Uruchomienia (Krok po kroku na prezentację)

Do poprawnego uruchomienia projektu wymagany jest język Python oraz biblioteka `aioquic`.

**Instalacja zależności:**
```bash
pip install aioquic

Part1 TCP
Otwórz pierwszy terminal i uruchom serwer TCP:
python server_tcp.py
(Oczekiwany wynik: "Serwer TCP/TLS nasłuchuje na 127.0.0.1:8443...")

Otwórz drugi terminal i uruchom klienta TCP:
python client_tcp.py
(Oczekiwany wynik: Logi potwierdzające przesłanie wiadomości w obu terminalach. Oznacza to udaną negocjację mTLS na protokole TCP).

Part2 QUIC
Zatrzymaj poprzednie skrypty (Ctrl+C). QUIC działa na warstwie UDP i natywnie wspiera TLS 1.3 .
W pierwszym terminalu uruchom serwer QUIC:

python server_quic.py
(Oczekiwany wynik: "Serwer QUIC nasłuchuje na 127.0.0.1:4433 (działa na UDP)...")

W drugim terminalu uruchom klienta QUIC:
python client_quic.py
(Oczekiwany wynik: Błyskawiczne zestawienie połączenia, wymiana certyfikatów i przesył logów testowych).

```
Dzięki super
