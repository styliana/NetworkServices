import asyncio
from aioquic.asyncio import serve
from aioquic.quic.configuration import QuicConfiguration
from aioquic.quic.events import StreamDataReceived
from aioquic.asyncio.protocol import QuicConnectionProtocol

class SerwerQUIC(QuicConnectionProtocol):
    def quic_event_received(self, event):
        if isinstance(event, StreamDataReceived):
            wiadomosc = event.data.decode('utf-8')
            print(f"Otrzymano wiadomość: {wiadomosc}")
            
            odpowiedz = "Serwer QUIC potwierdza odbiór! Szyfrowanie działa."
            self._quic.send_stream_data(event.stream_id, odpowiedz.encode('utf-8'), end_stream=True)
            self.transmit()

async def main():
    # Dodajemy ALPN - wymóg nowoczesnego QUIC/TLS 1.3
    konfiguracja = QuicConfiguration(
        is_client=False,
        alpn_protocols=["projekt-quic"] 
    )
    konfiguracja.load_cert_chain(certfile="server.crt", keyfile="server.key")

    print("Serwer QUIC nasłuchuje na 127.0.0.1:4433 (działa na UDP)...")
    await serve("127.0.0.1", 4433, configuration=konfiguracja, create_protocol=SerwerQUIC)
    await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())