# Dokumentacja Projektu 1: Starter Pack (Programowanie Usług Sieciowych)

## 1. Wstęp i cel projektu
Celem niniejszego projektu jest implementacja aplikacji sieciowej działającej w modelu klient-serwer. Rozwiązanie demonstruje niskopoziomową komunikację sieciową przy wykorzystaniu protokołu UDP. 

Projekt został przygotowany w sposób kompleksowy i realizuje następujące wymagania zaliczeniowe przedmiotu:
* **Wymagania na ocenę 4.0:** Zastosowanie gniazd surowych (ang. *raw sockets*). Oznacza to samodzielną implementację i obsługę komunikacji w warstwie sieciowej (3) oraz transportowej (4), bez pośrednictwa wysokopoziomowych bibliotek.
* **Wymagania na ocenę 4.5:** Nasłuchiwanie serwera na uprzywilejowanym porcie (port 80) przy jednoczesnym wykorzystaniu gniazd surowych w systemie Linux bez uprawnień administratora (konta `root`).
* **Wymagania na ocenę 5.0:** Odpowiednia konfiguracja systemowej zapory sieciowej (firewalla) do kontrolowania ruchu generowanego przez aplikację.

## 2. Środowisko uruchomieniowe i zarządzanie uprawnieniami
Z uwagi na specyfikę wymagań dotyczących zarządzania uprawnieniami w systemie Linux oraz konfiguracji zapory sieciowej `iptables`, projekt został przygotowany z myślą o środowisku opartym na systemie Ubuntu (np. poprzez WSL - Windows Subsystem for Linux).

**Ominięcie wymogu uprawnień administratora (root):**
Standardowo operacje takie jak otwarcie gniazda surowego lub rezerwacja portu poniżej 1024 wymagają uprawnień superużytkownika (komenda `sudo`). Aby spełnić wymóg realizacji tych zadań z poziomu zwykłego użytkownika, zastosowano mechanizm *Linux Capabilities*. 
W ramach konfiguracji środowiska skopiowano plik wykonywalny interpretera języka Python (tworząc plik `./moj_python`), a następnie nadano mu odpowiednie, punktowe uprawnienia za pomocą narzędzia `setcap`. Pozwala to na poprawne funkcjonowanie aplikacji przy jednoczesnym zachowaniu bezpieczeństwa reszty systemu operacyjnego.

## 3. Architektura Klienta (`client_raw.py`)
Z uwagi na wykorzystanie gniazd surowych na ocenę 4.0, aplikacja kliencka jest odpowiedzialna za samodzielne formowanie pełnych pakietów sieciowych. 

W kodzie klienta proces ten przebiega wieloetapowo:
1. **Budowa nagłówka IP (IPv4):** Ręczne zdefiniowanie parametrów takich jak wersja protokołu, długość pakietu oraz adresy źródłowy i docelowy (w przypadku testów lokalnych: `127.0.0.1`). Implementacja zawiera również algorytm wyliczający wymaganą sumę kontrolną (ang. *checksum*).
2. **Budowa nagłówka UDP:** Dołączenie informacji o porcie źródłowym oraz docelowym (port 80).
3. **Konstrukcja Payloadu:** Dołączenie właściwej wiadomości tekstowej na koniec pakietu.

Do serializacji struktury pakietu (konwersji typów liczbowych i tekstowych na ciąg bajtów zrozumiały dla interfejsów sieciowych) wykorzystano standardowy moduł `struct` języka Python, posługując się odpowiednimi łańcuchami formatującymi (np. `!BBHHHBBH4s4s`).

## 4. Architektura Serwera (`server_raw.py`)
Serwer został skonfigurowany do nasłuchiwania na uprzywilejowanym porcie 80, co realizuje założenia projektu na ocenę 4.5.

Aplikacja wykorzystuje gniazdo surowe. W związku z tym funkcja odbierająca (np. `recvfrom`) pobiera całą strukturę datagramu docierającego do interfejsu sieciowego – łącznie z nagłówkami dodanymi przez klienta. Aby wyodrębnić użyteczne dane (wiadomość tekstową), kod serwera implementuje następujący mechanizm parsowania:
1. Odrzucenie pierwszych 20 bajtów reprezentujących nagłówek IP.
2. Odrzucenie kolejnych 8 bajtów reprezentujących nagłówek UDP.
3. Odczyt i dekodowanie pozostałej części bufora jako docelowej wiadomości tekstowej.

## 5. Konfiguracja zapory sieciowej (Firewall)
W celu zrealizowania wymagań na ocenę 5.0, projekt obejmuje demonstrację manipulacji ruchem sieciowym za pomocą narzędzia `iptables`.

Scenariusz testowy zakłada utworzenie reguły w łańcuchu `INPUT`, która przechwytuje i bezwarunkowo odrzuca (`DROP`) pakiety protokołu UDP kierowane na port docelowy 80. Skutkuje to zablokowaniem widoczności komunikatów klienckich na serwerze, potwierdzając tym samym pełną kontrolę nad środowiskiem sieciowym.

---

## 6. Instrukcja uruchomienia i scenariusze testowe
Zaliczenie projektu przewiduje demonstrację działania aplikacji na żywo. Poniżej przedstawiono formalny scenariusz weryfikacji.

### Przygotowanie środowiska
Przed uruchomieniem głównych skryptów, należy przygotować lokalny interpreter i nadać mu wymagane uprawnienia *capabilities* (wykonywane jednorazowo): Na każdym terminalu u mnie wsl -d Ubuntu, po prostu ważne aby połączyć się w wsl.
```bash
# Wejście do folderu z projektem
cd ~/lab1/client-server

# Skopiowanie interpretera Pythona
cp /usr/bin/python3 ./moj_python

# Nadanie super-uprawnień (omija wymóg root'a)
sudo setcap 'cap_net_raw,cap_net_bind_service+ep' ./moj_python

# Krok 1: Odpalenie Serwera (Otwórz Terminal 1) - (Serwer "zawiśnie" i będzie czekał na pakiety)
cd ~/lab1/client-server
./moj_python server_raw.py

# Krok 2: Odpalenie Klienta (Otwórz Terminal 2) - (W Terminalu 1 powinieneś zobaczyć odebraną wiadomość.)
cd ~/lab1/client-server
./moj_python client_raw.py

# Krok 3: Demonstracja Firewalla na 5.0 (Otwórz Terminal 3) Wpisz komendę blokującą pakiety (wymaga hasła):
sudo iptables -A INPUT -p udp --dport 80 -j DROP

# Teraz wróć do Terminala 2 i odpal klienta ponownie (./moj_python client_raw.py). Pokaż prowadzącemu, że w Terminalu 1 (Serwer) nic się nie pojawia – firewall działa!

# Krok 4: Zdjęcie blokady (W Terminalu 3) - Zmieniamy flagę -A na -D (Delete), aby usunąć regułę:
sudo iptables -D INPUT -p udp --dport 80 -j DROP
'''

Odpal klienta w Terminalu 2 po raz ostatni. Serwer znowu radośnie odbierze pakiet!

W przypadku przykładu z ipv6 wystarczy, że połączysz się z wsl, w jednym terminalu (serwerowym) puścisz server_ipv6.py, a w drugim (klientowym) client_ipv6.py i gitara:) TPC i IPv6.


