import json

"""
File Template:
{
    tool: {
        entry_p: ,
        stop_p: ,
        take_ps: ,
        pos_side: ,
        move_stop_after: ,
        left_volume_to_fill: ,
        last_status:
    },
}
"""


def get_data():
    with open('orders.json', 'r') as f:
        orders = json.load(f)
        return orders


def get_data_for_order(tool):
    orders = get_data()

    try:
        return orders[tool]
    except Exception:
        return None


def put_data(new_orders):
    with open('orders.json', 'w') as f:
        json.dump(new_orders, f, indent=4)


def add_order(tool, entry_p, stop_p, take_ps, move_stop_after, left_volume_to_fill, last_status):
    orders = get_data()

    # WARNING
    # pos_side is calculated only when placing order, as after moving stop-loss to entry level, below code won't work
    pos_side = "LONG" if entry_p > stop_p else "SHORT"

    orders[tool] = {'entry_p': entry_p, 'stop_p': stop_p, 'take_ps': take_ps, 'pos_side': pos_side,
                    'move_stop_after': move_stop_after, 'left_volume_to_fill': left_volume_to_fill,
                    'last_status': last_status}

    put_data(orders)


def remove_order(order_id):
    orders = get_data()

    del orders[order_id]

    put_data(orders)


def update_left_volume(tool, left_volume_to_fill):
    orders = get_data()

    orders[tool]['left_volume_to_fill'] = left_volume_to_fill

    put_data(orders)


def update_last_status(tool, last_status):
    orders = get_data()

    orders[tool]['last_status'] = last_status

    put_data(orders)
