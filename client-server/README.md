# Dokumentacja Projektu: Starter Pack (PUS - Lab 1)

## Rozdział 1: O co w ogóle w tym chodzi? (Wstęp i cel)
Nasz projekt to tak zwany "starter pack" do programowania aplikacji sieciowych klienta i serwera. Celem było napisanie dwóch programów (Klienta i Serwera), które potrafią ze sobą "rozmawiać" przez sieć.

Od razu wycelowałyśmy w najwyższą ocenę, dlatego nasz projekt spełnia następujące, zaawansowane wymogi przedmiotu Programowanie Usług Sieciowych[cite: 2]:
* **Poziom 4.0:** Używamy tzw. gniazd surowych (raw sockets)[cite: 13]. Oznacza to, że musieliśmy osobiście zaprogramować komunikację w warstwie 3 i 4, nie polegając na gotowych bibliotekach, które robią to za nas.
* **Poziom 4.5:** Nasz serwer nasłuchuje na niskim, uprzywilejowanym porcie (dokładnie porcie 80), a my używamy gniazd surowych w systemie Linux całkowicie bez uprawnień konta administratora (root'a).
* **Poziom 5.0:** Sterujemy zaporą sieciową (firewallem), aby świadomie przepuszczać lub blokować ruch generowany przez naszą aplikację.



## Rozdział 2: Środowisko, czyli dlaczego uciekliśmy z Windowsa do Linuksa?
Zasady projektu wymagały zabawy uprawnieniami w systemie Linux oraz konfiguracji linuksowego firewalla[cite: 14, 15]. Zwykły Windows tego nie potrafi, dlatego użyliśmy **WSL (Windows Subsystem for Linux)**, czyli wirtualnego Ubuntu ukrytego w komputerze.

### Tajemnica pliku `moj_python`:
> Zwykle, aby otworzyć gniazdo surowe lub zająć port poniżej 1024, system wymaga komendy `sudo` (czyli bycia rootem). Projekt jednak tego zabrania. Dlatego skopiowaliśmy główny program Pythona do naszego folderu (tworząc plik `./moj_python`) i nadaliśmy mu punktowe, chirurgiczne uprawnienia zwane **Linux Capabilities** (`setcap`). Dzięki temu nasz skrypt ma supermoce sieciowe, ale reszta systemu jest bezpieczna.

## Rozdział 3: Anatomia Klienta (Jak ulepić własny pakiet)
Zwykłe programy sieciowe wysyłają tylko tekst, a system operacyjny sam pakuje go w "kopertę" (dodaje adresy IP, porty itp.). Ponieważ my używamy gniazd surowych na ocenę 4.0, system powiedział nam: "radźcie sobie same".

Nasz klient (`client_raw.py`) musi ręcznie zbudować cały pakiet danych:
* **Nagłówek IP:** Ręcznie wpisujemy wersję protokołu (IPv4), długość, skąd i dokąd leci pakiet (nasze `127.0.0.1`), a następnie wyliczamy skomplikowaną sumę kontrolną (checksum).
* **Nagłówek UDP:** Doklejamy informację o porcie źródłowym i porcie docelowym (port 80).
* **Payload (Wiadomość):** Na samym końcu doklejamy nasz tekst: *"Siema serwer..."*.



Do łączenia tych danych użyliśmy w Pythonie modułu `struct`. Pozwala on spakować zwykłe liczby i tekst w ciąg zer i jedynek (tzw. bajtów), używając formatów takich jak `!BBHHHBBH4s4s` (gdzie np. `B` to 1 bajt, a `H` to 2 bajty).

## Rozdział 4: Anatomia Serwera (Jak nasłuchiwać)
Nasz serwer (`server_raw.py`) jest ustawiony na nasłuchiwanie na porcie 80, co zalicza nam część wymogu na ocenę 4.5.

Gdy serwer odbiera wiadomość przez gniazdo surowe, dostaje absolutnie wszystko – całą "kopertę" od klienta. Żeby przeczytać samą wiadomość, serwer musi w kodzie "odciąć" początek tego pakietu:
1. Odrzuca pierwsze **20 bajtów** (bo tam jest nagłówek IP).
2. Odrzuca kolejne **8 bajtów** (bo tam jest nagłówek UDP).
3. Dopiero to, co zostaje od 28 bajtu do końca, to nasza właściwa wiadomość tekstowa, którą serwer wypisuje na ekranie.

## Rozdział 5: Ściana ognia, czyli sterowanie zaporą (Zadanie na 5.0)
Aby udowodnić, że kontrolujemy ruch sieciowy, użyliśmy systemowego narzędzia `iptables`.
Ponieważ komunikujemy się po protokole UDP na porcie 80, używamy komendy, która mówi systemowi: *"każdy wchodzący (`INPUT`) pakiet na port 80 (`--dport 80`) masz bezlitośnie zniszczyć (`DROP`)"*. Gdy blokada jest aktywna, serwer przestaje widzieć wiadomości od klienta.



---

## Rozdział 6: Ściągawka na zaliczenie (Krok po kroku)
Formą zaliczenia projektu jest prezentacja działającego kodu na żywo. Poniżej masz gotowy scenariusz tego, co wpisywać w terminalach Ubuntu.

### Przygotowanie
Zrób to przed zajęciami lub na samym początku, w głównym terminalu:
```bash
# Wejście do folderu z projektem
cd ~/lab1

# Skopiowanie interpretera Pythona
cp /usr/bin/python3 ./moj_python

# Nadanie super-uprawnień (omija wymóg root'a)
sudo setcap 'cap_net_raw,cap_net_bind_service+ep' ./moj_python

# Krok 1: Odpalenie Serwera (Otwórz Terminal 1) - (Serwer "zawiśnie" i będzie czekał na pakiety)
cd ~/lab1
./moj_python server_raw.py

# Krok 2: Odpalenie Klienta (Otwórz Terminal 2) - (W Terminalu 1 powinieneś zobaczyć odebraną wiadomość.)
cd ~/lab1
./moj_python client_raw.py

# Krok 3: Demonstracja Firewalla na 5.0 (Otwórz Terminal 3) Wpisz komendę blokującą pakiety (wymaga hasła):
sudo iptables -A INPUT -p udp --dport 80 -j DROP

# Teraz wróć do Terminala 2 i odpal klienta ponownie (./moj_python client_raw.py). Pokaż prowadzącemu, że w Terminalu 1 (Serwer) nic się nie pojawia – firewall działa!

# Krok 4: Zdjęcie blokady (W Terminalu 3) - Zmieniamy flagę -A na -D (Delete), aby usunąć regułę:
sudo iptables -D INPUT -p udp --dport 80 -j DROP
'''

Odpal klienta w Terminalu 2 po raz ostatni. Serwer znowu radośnie odbierze pakiet!
