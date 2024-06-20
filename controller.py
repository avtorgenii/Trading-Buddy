import bingx_exc as be

data = be._get_account_details()
print(data)

be.place_open_order("OP-USDT", 1.9253, 1.9253, 1.9104, [1.9452, 1.9478], 1)
