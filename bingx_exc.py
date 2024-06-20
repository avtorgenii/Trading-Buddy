from bingX.perpetual.v2 import PerpetualV2
from bingX.perpetual.v2.types import (Order, OrderType, Side, PositionSide, MarginType)

from db_manager import DBInterface
import math_helper as mh
import runtime_manager as rm

API_KEY = "g1bdJM9yg7bx07R614mv7zBRYxN05L10gglaiwsOWcX2JIqOEzhoZfzM75nVyZBNLp510vb0YxRgF8Zg5Sw"
SECRET_KEY = "1hdUt8cDl5o3K5mzJeX0k71OzhERLVWnT984jp5gsj4egmz4P4fTbvyoUPga3RQfhuGTchRA3T96lTIJOkQ"
ACCOUNT_NAME = "BingX"

client = PerpetualV2(api_key=API_KEY, secret_key=SECRET_KEY)

db_interface = DBInterface(ACCOUNT_NAME)

deposit, risk = db_interface.get_account_details()


def _get_account_details():
    """
    Returns the account details.
    :return: A tuple containing balance, unrealized profit, and available margin.
    """
    details = client.account.get_details()['balance']
    return {"deposit": deposit, "unrealized_pnl": float(details['unrealizedProfit']),
            "available_margin": float(details['availableMargin'])}


def _get_tool_precision_info(tool):
    info = client.market.get_contract_info(tool)
    return {"quantityPrecision": info['quantityPrecision'], "pricePrecision": info['pricePrecision'],
            "tradeMinQuantity": info['tradeMinQuantity']}


def _get_max_leverage(tool):
    info = client.trade.get_leverage(tool)
    return {"long": info["maxLongLeverage"], "short": info["maxShortLeverage"]}


def _get_current_leverage(tool):
    # Temporary, in future leverage should be fetched from frontend
    return _get_max_leverage(tool)["long"]


def _calc_position_volume_and_margin(tool, entry_p, stop_p):
    available_margin = _get_account_details()["available_margin"]
    leverage = _get_current_leverage(tool)

    precision_info = _get_tool_precision_info(tool)
    quantity_precision = precision_info['quantityPrecision']
    trade_min_quantity = precision_info['tradeMinQuantity']

    res = mh.calc_position_volume_and_margin(deposit, risk, entry_p, stop_p, available_margin, leverage,
                                             quantity_precision, trade_min_quantity)
    return res


def _switch_margin_mode_to_cross(tool):
    client.trade.change_margin_mode(symbol=tool, margin_type=MarginType.CROSSED)


def _place_primary_order(tool, trigger_p, entry_p, stop_p, pos_side, volume):
    order_side = Side.BUY if entry_p > stop_p else Side.SELL
    order_type = OrderType.TRIGGER_LIMIT

    order = Order(symbol=tool, side=order_side, positionSide=pos_side, quantity=volume, type=order_type,
                  price=entry_p, stopPrice=trigger_p)
    order_response = client.trade.create_order(order)

    return order_response['order']['orderId']


def place_open_order(tool, trigger_p, entry_p, stop_p, take_profits, move_stop_after):
    """
    :param tool: Tool to trade
    :param trigger_p: Price level on which to trigger placing limit order
    :param entry_p: Entry level
    :param stop_p: Stop-loss level
    :param take_profits: List of take-profits levels
    :param move_stop_after: After which take stop-loss will be moved to entry level
    :return:
    """
    _switch_margin_mode_to_cross(tool)

    pos_side = PositionSide.LONG if entry_p > stop_p else PositionSide.SHORT
    volume = _calc_position_volume_and_margin(tool, entry_p, stop_p)['volume']

    _place_primary_order(tool, trigger_p, entry_p, stop_p, pos_side, volume)

    # Adding order to runtime order book
    rm.add_order(tool, entry_p, stop_p, take_profits, move_stop_after, volume, "NEW")


def place_stop_loss_order(tool, stop_p, volume, pos_side):
    order_side = Side.SELL if pos_side == PositionSide.LONG else Side.BUY
    order_type = OrderType.STOP_MARKET

    order = Order(symbol=tool, side=order_side, positionSide=pos_side, quantity=volume, type=order_type,
                  stopPrice=stop_p)
    client.trade.create_order(order)

    print(f"PLACED SL: tp: {stop_p}, volume: {volume}")


def place_take_profit_orders(tool, take_profits, cum_volume, pos_side):
    order_side = Side.SELL if pos_side == PositionSide.LONG else Side.BUY
    order_type = OrderType.TAKE_PROFIT_MARKET

    quantity_precision = _get_tool_precision_info(tool)['quantityPrecision']

    volumes = mh.calc_take_profits_volumes(cum_volume, quantity_precision, len(take_profits))

    for take_profit, volume in zip(take_profits, volumes):
        order = Order(symbol=tool, side=order_side, positionSide=pos_side, quantity=volume, type=order_type,
                      stopPrice=take_profit)
        client.trade.create_order(order)

        print(f"PLACED TP: tp: {take_profit}, volume: {volume}")
