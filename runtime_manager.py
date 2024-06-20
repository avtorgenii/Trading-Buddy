import json

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
        left_volume_to_fill: ,
        last_status: ,
        breakeven: # True if stop-loss is moved nearby entry, False if not
    },
}
"""


def get_data():
    with open('orders.json', 'r') as f:
        orders = json.load(f)
        return orders


def put_data(new_orders):
    with open('orders.json', 'w') as f:
        json.dump(new_orders, f, indent=4)


def add_position(tool, entry_p, stop_p, take_ps, move_stop_after, primary_volume, last_status):
    orders = get_data()

    pos_side = "LONG" if entry_p > stop_p else "SHORT"

    orders[tool] = {'entry_p': entry_p, 'stop_p': stop_p, 'take_ps': take_ps,
                    'pos_side': pos_side,
                    'move_stop_after': move_stop_after, 'current_volume': 0,
                    'left_volume_to_fill': primary_volume,
                    'last_status': last_status, 'breakeven': False}

    put_data(orders)


def remove_position(tool):
    orders = get_data()

    del orders[tool]

    put_data(orders)


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
