import math


def floor_to_digits(number, digits):
    """
    Floor the number to a specified number of digits after the decimal point.

    :param number: The number to be floored.
    :type number: float
    :param digits: The number of digits to keep after the decimal point.
    :type digits: int
    :return: The floored number.
    :rtype: float
    """
    factor = 10 ** digits
    return math.floor(number * factor) / factor


def calc_position_volume_and_margin(deposit, risk, entry_p, stop_p, available_margin, leverage, quantity_precision,
                                    trade_min_quantity):
    diff_pips = abs(entry_p - stop_p)

    allowed_loss = deposit * risk / 100

    volume = floor_to_digits(allowed_loss / diff_pips, quantity_precision)

    required_margin = volume * entry_p / leverage

    if volume >= trade_min_quantity:
        if available_margin >= required_margin:
            return {"volume": volume, "margin": round(required_margin, 2)}
        else:
            allowed_volume = floor_to_digits(leverage * available_margin / entry_p, quantity_precision)
            return {"volume": allowed_volume,
                    "margin": round(allowed_volume * entry_p / leverage, 2)}
    else:
        return {"volume": 0, "margin": 0}


def calc_take_profits_volumes(volume, quantity_precision, num_take_profits):
    """
    Calculate the volumes for take profits.

    :param volume: Total volume to be distributed among take profits.
    :param quantity_precision: Precision for the volume.
    :param num_take_profits: Number of take profit targets.
    :return: List of volumes for take profits, largest volume first.
    """

    # Round function that respects the given precision
    def round_with_precision(value, precision):
        factor = 10 ** precision
        return round(value * factor) / factor

    # Calculate base volume for each take profit
    base_volume = volume / num_take_profits

    # Round the base volume according to the precision
    base_volume = round_with_precision(base_volume, quantity_precision)

    # Initialize the volumes list with the base volume
    take_profits_volumes = [base_volume] * num_take_profits

    # Calculate the remaining volume due to rounding
    remaining_volume = round_with_precision(volume - sum(take_profits_volumes), quantity_precision)

    # Adjust the first take profit volume to account for the remaining volume
    if remaining_volume != 0:
        take_profits_volumes[0] += remaining_volume

    # Sort volumes so the largest volume is first
    take_profits_volumes.sort(reverse=True)

    return take_profits_volumes
