import time
from bingX.perpetual.v2 import PerpetualV2
from bingX.perpetual.v2.types import HistoryOrder

import math_helper as mh


class Dealer:
    def __init__(self, deposit, risk):
        """
        Initializing BingX dealer with needed info.

        :param risk: Risk in percents.
        :type risk: float
        """

        self.API_KEY = "g1bdJM9yg7bx07R614mv7zBRYxN05L10gglaiwsOWcX2JIqOEzhoZfzM75nVyZBNLp510vb0YxRgF8Zg5Sw"
        self.SECRET_KEY = "1hdUt8cDl5o3K5mzJeX0k71OzhERLVWnT984jp5gsj4egmz4P4fTbvyoUPga3RQfhuGTchRA3T96lTIJOkQ"

        self.client = PerpetualV2(api_key=self.API_KEY, secret_key=self.SECRET_KEY)

        self.deposit = deposit
        self.risk = risk

    # data = client.account.get_details()
    # data = client.trade.get_orders_history(HistoryOrder(symbol="OCEAN-USDT",
    #                                                     startTime=1716422400000,
    #                                                     endTime=1716681600000,
    #                                                     limit=500))
    #
    # print(data)

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


dealer = Dealer(123.46, 3)

#data = dealer.get_account_details()
#data = dealer.calc_position_volume_and_margin("GMT-USDT", 0.2312, 0.2349)


print(data)
