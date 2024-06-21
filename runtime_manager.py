import json

from db_manager import DBInterface

import bingx_exc as be

"""
File Template:
{
    tool: {
        entry_p: ,
        stop_P:
        take_ps: [].
        pos_side: ,
        move_stop_after: , # After every take-profit decreases by 1, if is equal to one before decreasing - stop-loss is moved
        current_volume: ,
        left_volume_to_fill: , # For partial filling, doesn't work yet
        last_status: ,
        breakeven: ,# True if stop-loss is moved nearby entry, False if not
        start_time: ,
        end_time: ,
    },
}
"""

db_interface = DBInterface("BingX")


def get_data():
    with open('positions.json', 'r') as f:
        orders = json.load(f)
        return orders


def put_data(new_orders):
    with open('positions.json', 'w') as f:
        json.dump(new_orders, f, indent=4)


def add_position(tool, entry_p, stop_p, take_ps, move_stop_after, primary_volume):
    orders = get_data()

    pos_side = "LONG" if entry_p > stop_p else "SHORT"

    orders[tool] = {'entry_p': entry_p, 'stop_p': stop_p, 'take_ps': take_ps,
                    'pos_side': pos_side,
                    'move_stop_after': move_stop_after, 'current_volume': 0,
                    'left_volume_to_fill': primary_volume,
                    'last_status': "NEW", 'breakeven': False, 'start_time': None, 'end_time': None}

    put_data(orders)

    # INSERTING NEW ROW INTO DATABASE
    db_interface.insert_new_trade(tool=tool, pos_side=pos_side)


def close_position(tool):
    orders = get_data()

    add_additional_exchange_side_info_for_trade(tool)

    del orders[tool]

    put_data(orders)


def add_additional_exchange_side_info_for_trade(tool):
    start_time, end_time = get_info_for_position(tool, ['start_time', 'end_time'])

    price_of_entry, volume, price_of_exit, pnl, commission = be.get_position_info(tool, start_time, end_time)

    db_interface.update_last_trade_of_tool(tool, price_of_entry=price_of_entry, volume=volume, price_of_exit=price_of_exit,
                                           pnl_usdt=pnl, commission=commission)


def update_info_for_position(tool, **kwargs):
    """
    Update information for a specific order identified by the tool.

    Parameters:
    - tool (str): The tool identifier.
    - **kwargs: Arbitrary keyword arguments representing the fields to update and their new values.

    The structure of a primary order is as follows:

    primary_order_id: {
        tool (str): The name of the tool.
        entry_p (float): The entry price.
        stop (float): Stop-loss leveL.
        takes (list of floats): A list of take profit levels.
        pos_side (str): The position side (e.g., 'LONG' or 'SHORT').
        move_stop_after (float): The price after which the stop-loss is moved.
        current_volume (float): The current order volume.
        left_volume_to_fill (float): The volume left to fill.
        last_status (str): The last status of the order.
        breakeven (bool): Indicates if stop-loss is moved nearby entry level (True) or not (False).
        start_time (int): unix time of opening position
        end_time (int): unix time of closing position
    }

    Example:
    update_info_for_order('example_tool', left_volume_to_fill=10, last_status='FILLED')
    """
    orders = get_data()

    if tool in orders:
        for key, value in kwargs.items():
            if key in orders[tool]:
                orders[tool][key] = value
            else:
                print(f"Warning: '{key}' is not a valid attribute for the order.")

        put_data(orders)
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
        entry_p (float): The entry price.
        stop (float): Stop-loss leveL.
        takes (list of floats): A list of take profit levels.
        pos_side (str): The position side (e.g., 'LONG' or 'SHORT').
        move_stop_after (float): The price after which the stop-loss is moved.
        current_volume (float): The current order volume.
        left_volume_to_fill (float): The volume left to fill.
        last_status (str): The last status of the order.
        breakeven (bool): Indicates if stop-loss is moved nearby entry level (True) or not (False).
        start_time (int): unix time of opening position
        end_time (int): unix time of closing position
    }

    Example:
    info = get_info_for_order('order12345', ['tool', 'entry_p', 'last_status'])
    print(info)  # Output: ['example_tool', 1.2345, 'FILLED']
    """
    orders = get_data()

    try:
        order = orders[tool]
        output = []

        for param in desired_params:
            try:
                output.append(order[param])
            except KeyError:
                print(f"Parameter {param} does not exist")
                output.append(None)

        return output
    except KeyError:
        print(f"Position for {tool} does not exist")
        return [None] * len(desired_params)
