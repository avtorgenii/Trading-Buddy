from bingX.perpetual.v2 import PerpetualV2

from bingX.perpetual.v2.types import (Order, OrderType, Side, PositionSide, MarginType)

from db_creator import get_session
from db_creator import Account

import math_helper as mh


class Dealer:
    def __init__(self):
        """
        Initializing Exchange dealer with needed info.
        """

        print("Inited dealer")

        self.API_KEY = "g1bdJM9yg7bx07R614mv7zBRYxN05L10gglaiwsOWcX2JIqOEzhoZfzM75nVyZBNLp510vb0YxRgF8Zg5Sw"
        self.SECRET_KEY = "1hdUt8cDl5o3K5mzJeX0k71OzhERLVWnT984jp5gsj4egmz4P4fTbvyoUPga3RQfhuGTchRA3T96lTIJOkQ"
        self.ACCOUNT_NAME = "BingX"

        self.client = PerpetualV2(api_key=self.API_KEY, secret_key=self.SECRET_KEY)

        self.session = get_session(echo=False)

        account = self.session.query(Account).filter_by(account_name=self.ACCOUNT_NAME).first()

        self.deposit = account.deposit
        self.risk = account.risk

    def get_account_details(self):
        """
        Returns the account details.
        :return: A tuple containing balance, unrealized profit, and available margin.
        """
        details = self.client.account.get_details()['balance']

        return {"deposit": self.deposit, "unrealized_pnl": float(details['unrealizedProfit']),
                "available_margin": float(details['availableMargin'])}

    def get_tool_precision_info(self, tool):
        info = self.client.market.get_contract_info(tool)

        return {"quantityPrecision": info['quantityPrecision'], "pricePrecision": info['pricePrecision'],
                "tradeMinQuantity": info['tradeMinQuantity']}

    def get_max_leverage(self, tool):
        info = self.client.trade.get_leverage(tool)
        return {"long": info["maxLongLeverage"], "short": info["maxShortLeverage"]}

    def get_current_leverage(self, tool):
        # Temporary, in future leverage should be fetched from frontend
        return self.get_max_leverage(tool)["long"]

    def calc_position_volume_and_margin(self, tool, entry_p, stop_p):
        available_margin = self.get_account_details()["available_margin"]
        leverage = self.get_current_leverage(tool)

        precision_info = self.get_tool_precision_info(tool)
        quantity_precision = precision_info['quantityPrecision']
        trade_min_quantity = precision_info['tradeMinQuantity']

        res = mh.calc_position_volume_and_margin(self.deposit, self.risk, entry_p, stop_p, available_margin, leverage,
                                                 quantity_precision, trade_min_quantity)

        return res

    def switch_margin_mode_to_cross(self, tool):
        self.client.trade.change_margin_mode(symbol=tool, margin_type=MarginType.CROSSED)

    def place_primary_order(self, tool, trigger_p, entry_p, stop_p, pos_side):
        order_side = Side.BUY if entry_p > stop_p else Side.SELL
        volume = self.calc_position_volume_and_margin(tool, entry_p, stop_p)['volume']
        order_type = OrderType.TRIGGER_LIMIT

        order = Order(symbol=tool, side=order_side, positionSide=pos_side, quantity=volume, type=order_type,
                      price=entry_p, stopPrice=trigger_p)

        order_response = self.client.trade.create_order(order)

        return order_response['order']['orderId']

    def place_stop_loss_order(self, tool, stop_p, volume, pos_side):
        order_side = Side.SELL if pos_side == PositionSide.LONG else Side.BUY
        order_type = OrderType.STOP_MARKET

        order = Order(symbol=tool, side=order_side, positionSide=pos_side, quantity=volume, type=order_type,
                      stopPrice=stop_p, price=stop_p)

        self.client.trade.create_order(order)

    def place_order(self, tool, trigger_p, entry_p, stop_p, take_profits):
        self.switch_margin_mode_to_cross(tool)

        pos_side = PositionSide.LONG if entry_p > stop_p else PositionSide.SHORT

        primary_order_id = self.place_primary_order(tool, trigger_p, entry_p, stop_p, pos_side)



