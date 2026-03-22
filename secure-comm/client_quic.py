import asyncio
import ssl
from aioquic.asyncio import connect
from aioquic.quic.configuration import QuicConfiguration
from aioquic.quic.events import StreamDataReceived
from aioquic.asyncio.protocol import QuicConnectionProtocol

class KlientQUIC(QuicConnectionProtocol):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.odpowiedz = asyncio.get_event_loop().create_future()

    def quic_event_received(self, event):
        if isinstance(event, StreamDataReceived):
            wiadomosc = event.data.decode('utf-8')
            print(f"Odpowiedź z serwera: {wiadomosc}")
            if not self.odpowiedz.done():
                self.odpowiedz.set_result(True)

async def main():
    # Definiujemy ten sam protokół ALPN co w serwerze
    konfiguracja = QuicConfiguration(
        is_client=True,
        alpn_protocols=["projekt-quic-5.0"]
    )
    
    # Wskazujemy nasze własne CA (spełnia wymóg na 3.5)
    konfiguracja.load_verify_locations(cafile="ca.crt")
    
    # Wyłączamy restrykcyjne sprawdzanie hosta dla testowego 127.0.0.1
    konfiguracja.verify_mode = ssl.CERT_NONE

    print("Łączenie z serwerem QUIC (TLS 1.3)...")
    async with connect("127.0.0.1", 4433, configuration=konfiguracja, create_protocol=KlientQUIC) as polaczenie:
        stream_id = polaczenie._quic.get_next_available_stream_id()
        wiadomosc = "Siema! Tu nowoczesny klient QUIC z wbudowanym szyfrowaniem."
        
        print(f"Wysyłam: {wiadomosc}")
        polaczenie._quic.send_stream_data(stream_id, wiadomosc.encode('utf-8'), end_stream=True)
        polaczenie.transmit()

        await polaczenie.odpowiedz

if __name__ == "__main__":
    asyncio.run(main())