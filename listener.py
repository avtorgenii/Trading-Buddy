import json
import websocket
import gzip
import io

from bingX.perpetual.v2.other import Other
import runtime_manager as rm
import bingx_exc as be


class Listener:
    def __init__(self):
        self.API_KEY = "g1bdJM9yg7bx07R614mv7zBRYxN05L10gglaiwsOWcX2JIqOEzhoZfzM75nVyZBNLp510vb0YxRgF8Zg5Sw"
        self.SECRET_KEY = "1hdUt8cDl5o3K5mzJeX0k71OzhERLVWnT984jp5gsj4egmz4P4fTbvyoUPga3RQfhuGTchRA3T96lTIJOkQ"

        self.other = Other(api_key=self.API_KEY, secret_key=self.SECRET_KEY)

        listen_key_response = self.other.generate_listen_key()
        self.listen_key = listen_key_response['listenKey']
        self.ws_url = f"wss://open-api-swap.bingx.com/swap-market?listenKey={self.listen_key}"

        print(self.listen_key)

        self.ws = None

    def listen_for_events(self):
        def on_open(ws):
            print('WebSocket connected')

        def on_message(ws, message):
            compressed_data = gzip.GzipFile(fileobj=io.BytesIO(message), mode='rb')
            decompressed_data = compressed_data.read()
            utf8_data = decompressed_data.decode('utf-8')

            if utf8_data == "Ping":  # this is very important , if you receive 'Ping' you need to send 'Pong'
                print("Ping")
                ws.send("Pong")
            elif "ORDER_TRADE_UPDATE" in utf8_data:
                dict_data = json.loads(utf8_data)

                order = dict_data["o"]

                tool = order["s"]
                order_type = order["o"]
                direction = order["S"]
                volume = order["q"]
                avg_price = order["ap"]
                exec_type = order["x"]
                status = order["X"]

                data = rm.get_data_for_order(tool)
                print(f"ORDER DATA: {data}")

                # Checking if order is primary
                if order_type == "TRIGGER_LIMIT":
                    pos_side = data['pos_side']

                    if status == "FILLED":
                        print("ORDER IS FILLED")
                        rm.update_left_volume(tool, 0)
                        rm.update_last_status(tool, "FILLED")

                        take_profits = data['take_ps']
                        stop_loss = data['stop_p']
                        volume = data['left_volume_to_fill']

                        # Placing stop-loss
                        be.place_stop_loss_order(tool, stop_loss, volume, pos_side)

                        # Placing take-profits
                        be.place_take_profit_orders(tool, take_profits, volume, pos_side)







                    elif status == "PARTIALLY_FILLED":
                        # Should send notification for control from my side, as maybe some mistakes here due to rareness
                        # of this status
                        pass
                    elif status == "CANCELED":
                        rm.remove_order(tool)

                elif order_type == "STOP":
                    pass

                elif order_type == "TAKE_PROFIT":
                    pass

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


print("HELLO")

be.place_open_order("OP-USDT", 1.908, 1.9253, 1.9, [1.9452, 1.9478], 1)

listener = Listener()
listener.listen_for_events()
