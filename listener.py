import websocket
import gzip
import io

from bingX.perpetual.v2.other import Other


class Listener:
    def __init__(self):
        self.API_KEY = "g1bdJM9yg7bx07R614mv7zBRYxN05L10gglaiwsOWcX2JIqOEzhoZfzM75nVyZBNLp510vb0YxRgF8Zg5Sw"
        self.SECRET_KEY = "1hdUt8cDl5o3K5mzJeX0k71OzhERLVWnT984jp5gsj4egmz4P4fTbvyoUPga3RQfhuGTchRA3T96lTIJOkQ"

        self.other = Other(api_key=self.API_KEY, secret_key=self.SECRET_KEY)

        listen_key_response = self.other.generate_listen_key()
        if 'listenKey' in listen_key_response:
            self.listen_key = listen_key_response['listenKey']
            self.ws_url = f"wss://open-api-swap.bingx.com/swap-market?listenKey={self.listen_key}"
        else:
            raise Exception("Failed to generate listen key")

        print(self.listen_key)

        self.ws = None

        self.listen_for_events()

    def listen_for_events(self):
        def on_open(ws):
            print('WebSocket connected')

        def on_message(ws, message):
            compressed_data = gzip.GzipFile(fileobj=io.BytesIO(message), mode='rb')
            decompressed_data = compressed_data.read()
            utf8_data = decompressed_data.decode('utf-8')
            print(f"From on_message: {utf8_data}")  # this is the message you need
            if utf8_data == "Ping":  # this is very important , if you receive 'Ping' you need to send 'Pong'
                ws.send("Pong")
            elif utf8_data["e"] == "ORDER_TRADE_UPDATE":
                order = utf8_data["e"]["o"]

                tool = order["s"]
                order_id = order["i"]
                direction = order["S"]
                volume = order["q"]
                avg_price = order["ap"]
                status = order["X"]

        def on_error(ws, error):
            print(f"Error: {error}")

        def on_close(ws, close_status_code, close_msg):
            print(f'The connection is closed! Status code: {close_status_code}, Close message: {close_msg}')

        self.ws = websocket.WebSocketApp(
            self.ws_url,
            on_open=on_open,
            on_message=on_message,
            on_error=on_error,
            on_close=on_close,
        )
        self.ws.run_forever()


listener = Listener()
