import time


from bingX.perpetual.v2 import PerpetualV2
from bingX.perpetual.v2.types import HistoryOrder


API_KEY = "GyQBzygsWyTJhHKZ8FHsnSKneOYycqsz91mmQBtL24dTaFhG8yj1P8iZjKqZlmMUACVtr3sXpqK9YcXnwXYKQ"
SECRET_KEY = "dnsdD63a07Or1i93ad7WeQaD7QqdywzEYD29i8crCdSFyhj23Tzf1TrrMR8XLJmqzoKJEvzHzMUTCPPj5Xfw"

client = PerpetualV2(api_key=API_KEY, secret_key=SECRET_KEY)

# data = client.account.get_details()
data = client.trade.get_orders_history(HistoryOrder(symbol="OCEAN-USDT",
                                                    startTime=1716422400000,
                                                    endTime=1716681600000,
                                                    limit=500))

print(data)