import json
import os
import time
from os import getenv

import requests

from app.db_manager import DBInterface

"""
File Template:
{
    tool: {
        entry_p:
        stop_P:
        take_ps: [],
        pos_side: ,
        move_stop_after: , # After every take-profit decreases by 1, if is equal to one before decreasing - stop-loss is moved
        primary_volume: ,
        current_volume: ,
        left_volume_to_fill: , # For partial filling
        last_status: ,
        breakeven: ,# True if stop-loss is moved nearby entry, False if not
        pnl: ,
        commission: 
        start_time: 
        leverage: ,
        trigger_p: ,
        cancel_levels: [] # First is for overhigh/overlow, second is for take-profit level
        fill_history: [[avg_price, volume], [..., ...]] - # For calculating result entry_p for cases with partial_filling of position
    },
}
"""

db_interface = DBInterface("BingX")

POS_PATH = os.getenv("POSITIONS_PATH", "positions.json")


def get_data():
    with open(POS_PATH, 'r') as f:
        positions = json.load(f)
        return positions


def put_data(new_positions):
    with open(POS_PATH, 'w') as f:
        json.dump(new_positions, f, indent=4)


put_data({})


def add_position(tool, entry_p, stop_p, take_ps, move_stop_after, primary_volume, risk, leverage, trigger_p):
    orders = get_data()

    pos_side = "LONG" if entry_p > stop_p else "SHORT"

    orders[tool] = {'entry_p': entry_p, 'stop_p': stop_p, 'take_ps': take_ps,
                    'pos_side': pos_side,
                    'move_stop_after': move_stop_after, 'current_volume': 0.0,
                    'left_volume_to_fill': primary_volume, 'primary_volume': primary_volume,
                    'last_status': "NEW", 'breakeven': False, 'pnl': 0.0, 'commission': 0.0, 'leverage': leverage,
                    'trigger_p': trigger_p, 'cancel_levels': [], 'start_time': int(time.time()), 'fill_history': []}

    put_data(orders)

    # INSERTING NEW ROW INTO DATABASE
    side = "лонг" if entry_p > stop_p else "шорт"
    db_interface.insert_new_trade(tool=tool.replace("-USDT", ""), side=side, risk_usdt=risk)


def stop_price_listener(tool: str):
    port = int(getenv("PORT", 8080))
    base_url = os.getenv("SITE_URL", f"http://127.0.0.1:{port}")
    route = "/stop-price-listener/"
    url = base_url + route

    cancel_data = {"tool": tool}
    response = requests.post(url, json=cancel_data)

    if response.status_code == 200:
        print("Price listener stopped successfully:", response.json())
    else:
        print(f"Error stopping price listener: {response.status_code}, {response.json()}")


def close_position(tool):
    """
    For positions closing and automatic cancelation of orders when reached take-profit level, their data is being saved into database
    """
    orders = get_data()

    pnl, commission, primary_volume, start_time, last_status = get_info_for_position(tool,
                                                                                     ['pnl', 'commission',
                                                                                      'primary_volume', 'start_time',
                                                                                      'last_status'])
    # If trade was canceled automatically, its status doesn't change from the beginning
    if last_status == "NEW":
        primary_volume = None
        pnl = None
        commission = None

    db_interface.update_last_trade_of_tool(tool.replace("-USDT", ""), volume=primary_volume, pnl_usdt=pnl,
                                           commission=commission,
                                           start_time=start_time,
                                           end_time=int(time.time()))

    # Updating run-time json
    del orders[tool]
    put_data(orders)

    stop_price_listener(tool)


def cancel_position(tool):
    """
    For manual cancelation of position, or cancelation via overhigh/overlow
    """
    orders = get_data()

    del orders[tool]
    put_data(orders)

    db_interface.remove_last_trade_of_tool(tool.replace("-USDT", ""))

    # Deleting price listener
    stop_price_listener(tool)


def get_entry_price_for_position(tool):
    history, = get_info_for_position(tool, ['fill_history'])

    res_price = 0
    total_volume = 0

    for fill in history:
        avg_price, volume = fill

        total_volume += volume

        res_price += avg_price * volume

    return res_price / total_volume


def update_info_for_position(tool, **kwargs):
    """
    Update information for a specific order identified by the tool.

    Parameters:
    - tool (str): The tool identifier.
    - **kwargs: Arbitrary keyword arguments representing the fields to update and their new values.

    The structure of a primary order is as follows:

    primary_order_id: {
        tool (str): The name of the tool.
        stop (float): Stop-loss leveL.
        takes (list of floats): A list of take profit levels.
        pos_side (str): The position side (e.g., 'LONG' or 'SHORT').
        move_stop_after (float): The price after which the stop-loss is moved.
        primary_volume (float): Initial volume for position.
        current_volume (float): The current order volume.
        left_volume_to_fill (float): The volume left to fill.
        last_status (str): The last status of the order.
        breakeven (bool): Indicates if stop-loss is moved nearby entry level (True) or not (False).
        pnl (float): Total current realized pnl of position
        commission (float): Total current commission of position
        cancel_levels (List[float]): Overhigh/overlow and take-profit value for cancelation of order
        fill_history (List[List[float]]): [[avg_price, volume], [..., ...]] - # For calculating result entry_p for cases with partial_filling of position
    }

    Example:
    update_info_for_order('example_tool', left_volume_to_fill=10, last_status='FILLED')
    """
    positions = get_data()

    if tool in positions:
        for key, value in kwargs.items():
            if key in positions[tool]:
                positions[tool][key] = value
            else:
                print(f"Warning: '{key}' is not a valid attribute for the order.")

        put_data(positions)
    else:
        print(f"Warning: No order found for tool '{tool}'")


def get_info_for_position(tool, desired_params):
    """
    Retrieve specific information for a given primary order ID.

    Parameters:
    - primary_order_id (str): The unique identifier for the primary order.
    - desired_params (list of str): List of parameter names to retrieve values for.

    Returns:
    - list: A list containing the values of the desired parameters in the same order as provided. If a parameter does not exist, its value will be None.

    The structure of a primary order is as follows:

    primary_order_id: {
        tool (str): The name of the tool.
        stop (float): Stop-loss leveL.
        takes (list of floats): A list of take profit levels.
        pos_side (str): The position side (e.g., 'LONG' or 'SHORT').
        move_stop_after (float): The price after which the stop-loss is moved.
        primary_volume (float): Initial volume for position.
        current_volume (float): The current order volume.
        left_volume_to_fill (float): The volume left to fill.
        last_status (str): The last status of the order.
        breakeven (bool): Indicates if stop-loss is moved nearby entry level (True) or not (False).
        pnl (float): Total current realized pnl of position
        commission (float): Total current commission of position
        start_time (float): Start time in unix
        leverage (int):
        trigger_p (float):
        fill_history (List[List[float]]): [[avg_price, volume], [..., ...]] - # For calculating result entry_p for cases with partial_filling of position
    }

    Example:
    info = get_info_for_order('order12345', ['tool', 'entry_p', 'last_status'])
    print(info)  # Output: ['example_tool', 1.2345, 'FILLED']
    """
    positions = get_data()

    try:
        position = positions[tool]
        output = []

        for param in desired_params:
            try:
                output.append(position[param])
            except KeyError:
                print(f"Parameter {param} does not exist")
                output.append(None)

        return output
    except KeyError:
        #print(f"Position for {tool} does not exist")
        return [None] * len(desired_params)
