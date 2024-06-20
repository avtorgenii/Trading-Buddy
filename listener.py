import json
import time

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
                print("ORDER UPDATE")

                dict_data = json.loads(utf8_data)

                print(dict_data)

                order = dict_data["o"]

                tool = order["s"]
                order_type = order["o"]
                order_id = str(order["i"])
                direction = order["S"]
                volume = float(order["q"])
                avg_price = float(order["ap"])
                exec_type = order["x"]
                status = order["X"]

                # Checking if order is primary
                if order_type == "TRIGGER_LIMIT":
                    if status == "FILLED":
                        print("ORDER IS FILLED")

                        rm.update_info_for_position(tool, entry_p=avg_price, left_volume_to_fill=0, last_status="FILLED",
                                                    current_volume=volume)

                        pos_side, takes, stop = rm.get_info_for_position(tool, ['pos_side', 'take_ps', 'stop_p'])

                        # Placing stop-loss
                        be.place_stop_loss_order(tool, stop, volume, pos_side)

                        # Placing take-profits
                        be.place_take_profit_orders(tool, takes, volume, pos_side)

                    elif status == "CANCELED":
                        rm.remove_position(tool)

                    # elif status == "PARTIALLY_FILLED":
                    #     Should send notification for control from my side, as maybe some mistakes here due to rareness
                    #     of this status
                    #     pass

                elif order_type == "STOP":
                    rm.remove_position(tool)

                elif order_type == "TAKE_PROFIT_MARKET" and status == "TRIGGERED":
                    print("TRIGGERED TAKE_PROFIT")
                    # Cancel previous stop-loss and place new if stop-loss wasn't moved yet
                    breakeven, = rm.get_info_for_position("OP-USDT", ['breakeven'])
                    if not breakeven:
                        print("POSITION NOT IN BREAKEVEN YET")
                        be.cancel_stop_loss_for_tool(tool)

                        # Decreasing volume for new stop-loss as take-profit already fixed some volume of position
                        volume_for_stop_loss = rm.get_info_for_position(tool, ['current_volume'])[0] - volume

                        rm.update_info_for_position(tool, current_volume=volume_for_stop_loss)

                        print(f"Volume for breakeven: {volume_for_stop_loss}")

                        # If it was the last take - remove order from run-time book?
                        if volume_for_stop_loss == 0:
                            rm.remove_position(tool)
                            print("REMOVED POSITION FROM BOOK")
                        else:
                            # Moving stop-loss to breakeven
                            pos_side, move_stop_after = rm.get_info_for_position(tool, ['pos_side', 'move_stop_after'])

                            print(f"MOVE STOP AFTER: {move_stop_after}")

                            if move_stop_after == 1:
                                print(f"PLACING NEW BREAKEVEN for {tool}, pos_side: {pos_side}")

                                entry_p, = rm.get_info_for_position(tool, ['entry_p'])

                                be.place_stop_loss_order(tool, entry_p, volume_for_stop_loss, pos_side)
                                rm.update_info_for_position(tool, move_stop_after=move_stop_after - 1, breakeven=True)

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

# Short
#be.place_open_order("OP-USDT", 1.8307, 1.8, 1.87, [1.8302, 1.83], 1)
# Long
be.place_open_order("OP-USDT", 1.8342, 1.9, 1.8, [1.8348, 1.85], 1)

listener = Listener()
listener.listen_for_events()
