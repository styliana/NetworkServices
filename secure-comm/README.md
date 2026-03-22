# Projekt 2: Bezpieczna Komunikacja (TCP & QUIC z mTLS)

## 📌 O projekcie
Niniejszy projekt realizuje wszystkie wymagania z zadania "Projekt 2: Bezpieczna komunikacja" na ocenę 5.0 [cite: 20-27]. Implementacja demonstruje zestawienie bezpiecznych, szyfrowanych kanałów komunikacji z wykorzystaniem zarówno klasycznego protokołu **TCP** (z biblioteką `ssl`), jak i nowoczesnego protokołu **QUIC** (z biblioteką `aioquic`). 

Kluczowym elementem projektu jest autorska infrastruktura PKI (Public Key Infrastructure) oraz wdrożenie **obustronnego uwierzytelniania (mTLS)**, gdzie zarówno serwer, jak i klient muszą wylegitymować się ważnym certyfikatem podpisanym przez zaufane Centrum Certyfikacji (CA)[cite: 22, 24].

---

## 🎯 Zrealizowane Wymagania (Kaskadowo)

1. **Ocena 3.0:** Implementacja klienta i serwera TCP wykorzystujących szyfrowanie TLS[cite: 21].
2. **Ocena 3.5:** Stworzenie własnego, lokalnego Centrum Certyfikacji (Root CA), wygenerowanie własnych kluczy i certyfikatów oraz użycie ich w kodzie[cite: 22].
3. **Ocena 4.0:** Zastosowanie obustronnego uwierzytelniania (Mutual TLS). Serwer twardo weryfikuje certyfikat klienta przed nawiązaniem połączenia[cite: 24].
4. **Ocena 4.5 & 5.0:** Implementacja klienta i serwera w oparciu o protokół QUIC (działający na warstwie UDP) z wbudowanym TLS 1.3 .

---

## 🔐 Infrastruktura PKI (Jak u nas działają certyfikaty?)

Aby zrealizować obustronne uwierzytelnianie bez ostrzeżeń o niezaufanych wystawcach, stworzyliśmy własny urząd certyfikacji (Root CA) i wydaliśmy certyfikaty dla podmiotów końcowych.

### Słowniczek plików:
* **`.key` (Klucz prywatny):** Ściśle tajny, asymetryczny klucz kryptograficzny (np. RSA 2048-bit). Służy do deszyfrowania danych oraz składania podpisów cyfrowych.
* **`.csr` (Certificate Signing Request):** Żądanie podpisania certyfikatu. Zawiera klucz publiczny podmiotu i jego dane (np. Common Name).
* **`.crt` (Certyfikat X.509):** Publiczny dokument poświadczający tożsamość, na którym urząd CA złożył swój podpis cyfrowy.

### Proces generowania w naszym projekcie (Krok po kroku):
1. **Inicjalizacja CA:** Wygenerowaliśmy klucz prywatny naszego urzędu (`ca.key`) i na jego podstawie utworzyliśmy publiczny, samopodpisany certyfikat root (`ca.crt`)[cite: 22].
2. **Klucze podmiotów:** Klient i Serwer wygenerowali własne klucze prywatne (`client.key`, `server.key`).
3. **Wnioski CSR:** Na podstawie kluczy prywatnych wygenerowano żądania podpisania (`.csr`).
4. **Wystawienie certyfikatów:** Nasze CA (`ca.key`) podpisało kryptograficznie żądania, tworząc prawomocne certyfikaty końcowe (`client.crt`, `server.crt`).

Podczas łączenia się, obie strony wysyłają sobie pliki `.crt` i weryfikują je względem wczytanego wzoru zaufanego urzędu (`ca.crt`).

---

## ⚙️ Wyjaśnienie kluczowych elementów kodu

Mechanika bezpieczeństwa (mTLS) opiera się na odpowiedniej konfiguracji kontekstu TLS w skryptach Pythona:

* `load_cert_chain(certfile="...", keyfile="...")`  
  *Ładuje do pamięci certyfikat podmiotu oraz jego klucz prywatny, aby podmiot mógł udowodnić swoją tożsamość drugiej stronie.*
* `load_verify_locations(cafile="ca.crt")`  
  *Wskazuje aplikacji, że ma ufać **tylko i wyłącznie** certyfikatom, które zostały cyfrowo podpisane przez ten konkretny plik Root CA.*
* `verify_mode = ssl.CERT_REQUIRED`  
  *Najważniejsza flaga dla oceny 4.0. Wymusza na serwerze twarde żądanie certyfikatu od klienta. Jeśli klient go nie wyśle (lub wyśle niepodpisany przez nasze CA), połączenie zostanie natychmiast zerwane[cite: 24].*
* `alpn_protocols=["projekt-quic-5.0"]` *(tylko QUIC)* *Application-Layer Protocol Negotiation. Zabezpiecza przed łączeniem się z naszym serwerem niekompatybilnych klientów, wymuszając z góry określony protokół aplikacyjny.*

---

## 🚀 Instrukcja Uruchomienia (Krok po kroku na prezentację)

Do poprawnego uruchomienia projektu wymagany jest język Python oraz biblioteka `aioquic`.

**Instalacja zależności:**
```bash
pip install aioquic