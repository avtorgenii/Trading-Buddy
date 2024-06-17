from decimal import Decimal, ROUND_DOWN


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
    context = Decimal(number).scaleb(-digits).quantize(Decimal('1'), rounding=ROUND_DOWN).scaleb(digits)
    return float(context)


def calc_position_volume_and_margin(deposit, risk, entry_p, stop_p, available_margin, leverage, quantity_precision,
                                    trade_min_quantity):
    diff_pips = abs(entry_p - stop_p)

    allowed_loss = deposit * risk / 100

    volume = floor_to_digits(allowed_loss / diff_pips, quantity_precision)

    required_margin = volume * entry_p / leverage

    if volume >= trade_min_quantity:
        if available_margin >= required_margin:
            return volume, round(required_margin, 2)
        else:
            allowed_volume = floor_to_digits(available_margin / entry_p, quantity_precision)
            return allowed_volume, round(available_margin - allowed_volume * entry_p, 2)
    else:
        return 0, 0
