from bingx_exc import Dealer

dealer = Dealer()

data = dealer.get_account_details()
print(data)

# dealer.place_order("GMT-USDT", 0.1627, 0.165, 0.1509, [0.16])