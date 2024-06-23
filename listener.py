import json
import time

import websocket
import gzip
import io
import schedule

from bingX.perpetual.v2.other import Other
import runtime_manager as rm
import bingx_exc as be


class Listener:
    def __init__(self):
        self.API_KEY = "g1bdJM9yg7bx07R614mv7zBRYxN05L10gglaiwsOWcX2JIqOEzhoZfzM75nVyZBNLp510vb0YxRgF8Zg5Sw"
        self.SECRET_KEY = "1hdUt8cDl5o3K5mzJeX0k71OzhERLVWnT984jp5gsj4egmz4P4fTbvyoUPga3RQfhuGTchRA3T96lTIJOkQ"

        self.ws_url = "wss://open-api-swap.bingx.com/swap-market"

        self.ws = None

    def decode_data(self, message):
        compressed_data = gzip.GzipFile(fileobj=io.BytesIO(message), mode='rb')
        decompressed_data = compressed_data.read()

        return decompressed_data.decode('utf-8')

    def on_open(self, ws):
        print(f'{self.__class__.__name__}: WebSocket connected')

    def on_message(self, ws, message):
        utf8_data = self.decode_data(message)

        if utf8_data == "Ping":  # this is very important , if you receive 'Ping' you need to send 'Pong'
            print(f"{self.__class__.__name__}: Ping")
            ws.send("Pong")

        return utf8_data

    def on_error(self, ws, error):
        print(f"{self.__class__.__name__}: Error: {error}")

    def on_close(self, ws, close_status_code, close_msg):
        print(
            f'{self.__class__.__name__}: The connection is closed! Status code: {close_status_code}, Close message: {close_msg}')

    def listen_for_events(self):
        self.ws = websocket.WebSocketApp(
            self.ws_url,
            on_open=self.on_open,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close,
        )
        self.ws.run_forever()

    def stop_listening(self):
        #print("LISTENER:       stop_listening() fired")
        self.ws.close()


class OrderListener(Listener):
    def extend_listen_key_validity(self):
        self.other.extend_listen_key_validity_period(self.listen_key)

        print(f"{self.__class__.__name__}: Extended listen key validity: {self.listen_key}")

    def run_scheduler(self):
        print(self.listen_key)
        schedule.every(30).minutes.do(self.extend_listen_key_validity)

    def __init__(self):
        super().__init__()

        self.other = Other(api_key=self.API_KEY, secret_key=self.SECRET_KEY)

        listen_key_response = self.other.generate_listen_key()
        self.listen_key = listen_key_response['listenKey']
        self.ws_url = f"wss://open-api-swap.bingx.com/swap-market?listenKey={self.listen_key}"

        self.run_scheduler()

        self.ws = None

    def extract_info_from_utf_data(self, data):
        dict_data = json.loads(data)

        order = dict_data["o"]

        tool = order["s"]
        order_type = order["o"]
        volume = float(order["q"])
        avg_price = float(order["ap"])
        status = order["X"]
        pnl = float(order["rp"])
        commission = float(order["n"])

        return tool, order_type, volume, avg_price, status, pnl, commission

    def on_fill_primary_order(self, tool, avg_price, volume, new_commission):
        print(f"{self.__class__.__name__}: ORDER IS FILLED")

        left_volume_to_fill, commission = rm.get_info_for_position(tool, ['left_volume_to_fill', 'commission'])

        rm.update_info_for_position(tool, entry_p=avg_price, left_volume_to_fill=left_volume_to_fill - volume,
                                    last_status="FILLED",
                                    current_volume=volume, commission=commission + new_commission,
                                    start_time=int(time.time()))

        pos_side, takes, stop, ls = rm.get_info_for_position(tool, ['pos_side', 'take_ps', 'stop_p', 'last_status'])

        print(f"LAST                    STATUS OF           POSITION IS NOW: {ls}")

        # Placing stop-loss
        be.place_stop_loss_order(tool, stop, volume, pos_side)

        # Placing take-profits
        be.place_take_profit_orders(tool, takes, volume, pos_side)

        # Stopping price listener
        rm.stop_price_listener(tool)

    def on_partial_fill_primary_order(self, tool, new_commission):
        # Should send notification for control from my side, as maybe some mistakes here due to rareness
        # of this status

        print(f"{self.__class__.__name__}: ORDER IS PARTIALLY FILLED")

        # Set start_time only if it wasn't set yet
        start_time, commission = rm.get_info_for_position(tool, ['start_time', 'commission'])

        if start_time is None:
            rm.update_info_for_position(tool, commission=commission + new_commission,
                                        last_status="PARTIALLY_FILLED")

        # Stopping price listener
        rm.stop_price_listener(tool)

    def on_cancel_primary_order(self, tool):
        rm.update_info_for_position(tool, last_status="CANCELLED")
        rm.close_position(tool)

    def on_stop(self, tool, new_pnl, new_commission):
        commission, pnl = rm.get_info_for_position(tool, ['commission', 'pnl'])

        rm.update_info_for_position(tool, pnl=pnl + new_pnl, commission=commission + new_commission, last_status="STOP")
        rm.close_position(tool)

    def on_take_profit(self, tool, volume, new_pnl, new_commission, status):
        if status == "PARTIALLY_FILLED" or status == "FILLED":
            print(f"{self.__class__.__name__}: FILLING TAKE_PROFIT")

            # Cancel previous stop-loss and place new if stop-loss wasn't moved yet
            breakeven, pnl, commission = rm.get_info_for_position(tool, ['breakeven', 'pnl', 'commission'])

            rm.update_info_for_position(tool, pnl=pnl + new_pnl, commission=commission + new_commission)

            if not breakeven:
                # Decreasing volume for new stop-loss as take-profit already fixed some volume of position
                volume_for_stop_loss = rm.get_info_for_position(tool, ['current_volume'])[0] - volume

                rm.update_info_for_position(tool, current_volume=volume_for_stop_loss, last_status="TAKE_PROFIT")

                # If it was the last take - remove order from run-time book?
                if volume_for_stop_loss == 0:
                    rm.close_position(tool)
                else:
                    # Moving stop-loss to breakeven
                    pos_side, move_stop_after = rm.get_info_for_position(tool, ['pos_side', 'move_stop_after'])

                    if move_stop_after == 1:
                        be.cancel_stop_loss_for_tool(tool)

                        entry_p, = rm.get_info_for_position(tool, ['entry_p'])

                        be.place_stop_loss_order(tool, entry_p, volume_for_stop_loss, pos_side)
                        rm.update_info_for_position(tool, move_stop_after=move_stop_after - 1, breakeven=True)

    def on_message(self, ws, message):
        utf8_data = super().on_message(ws, message)

        schedule.run_pending()  # Extending listen key validity

        if utf8_data != "Ping":
            if "ORDER_TRADE_UPDATE" in utf8_data:
                print(f"{self.__class__.__name__}: ORDER UPDATE")

                tool, order_type, volume, avg_price, status, pnl, commission = self.extract_info_from_utf_data(
                    utf8_data)

                print(f"DATA FOR NEW                       ORDERRRRRRRRRRRRRRRRRRR: {utf8_data}")

                if order_type == "TRIGGER_LIMIT" or order_type == "LIMIT":
                    if status == "FILLED":
                        self.on_fill_primary_order(tool, avg_price, volume, commission)

                    elif status == "CANCELED":
                        # Position cancelation will work from exchange site too - not yet
                        self.on_cancel_primary_order(tool)

                    elif status == "PARTIALLY_FILLED":
                        self.on_partial_fill_primary_order(tool, commission)

                elif order_type == "STOP":  # CHECK IS THIS WORKS IN FUTURE
                    self.on_stop(tool, pnl, commission)

                elif order_type == "TAKE_PROFIT_MARKET":
                    self.on_take_profit(tool, volume, pnl, commission, status)

    def listen_for_events(self):
        self.ws = websocket.WebSocketApp(
            self.ws_url,
            on_open=self.on_open,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close,
        )
        self.ws.run_forever()


class PriceListener(Listener):
    def __init__(self, tool):
        super().__init__()

        self.tool = tool

        self.CHANNEL = {"id": "24dd0e35-56a4-4f7a-af8a-394c7060909c", "reqType": "sub", "dataType": f"{tool}@lastPrice"}

    def check_price_for_order_cancelation(self, price):
        over_and_take, pos_side = rm.get_info_for_position(self.tool, ['cancel_levels', 'pos_side'])

        try:
            over, take = over_and_take

            if pos_side == "LONG":
                if price <= over:
                    be.cancel_primary_order_for_tool(self.tool, True)
                elif price >= take:
                    be.cancel_primary_order_for_tool(self.tool, False)
            else:
                if price <= over:
                    be.cancel_primary_order_for_tool(self.tool, True)
                elif price >= take:
                    be.cancel_primary_order_for_tool(self.tool, False)

        except Exception as e:
            #print(f"{__class__.__name__}, {self.tool}: Cancelation levels for {self.tool} not specified: {e}")
            pass

    def on_open(self, ws):
        super().on_open(ws)
        subStr = json.dumps(self.CHANNEL)
        ws.send(subStr)
        #(f"{self.__class__.__name__}, {self.tool}: Subscribed to :", subStr)

    def on_message(self, ws, message):
        utf8_data = super().on_message(ws, message)

        if utf8_data != "Ping":
            dict_data = json.loads(utf8_data)

            price = float(dict_data["data"]["c"])

            if price is not None:
                self.check_price_for_order_cancelation(price)

    def listen_for_events(self):
        self.ws = websocket.WebSocketApp(
            self.ws_url,
            on_open=self.on_open,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close,
        )
        self.ws.run_forever()


"""DEBUG"""
if __name__ == "__main__":
    # Short
    # be.place_open_order("OP-USDT", 1.8307, 1.8, 1.87, [1.8302, 1.83], 1)
    # Long
    # res = be.place_open_order("OP-USDT", 1.818, 1.8146, 1.7776, [1.8348, 1.85], 1, 50, 1.5)
    # print(res)
    # listener = OrderListener()
    # listener.listen_for_events()
    # listener = PriceListener("OP-USDT")
    # listener.listen_for_events()

    pass
