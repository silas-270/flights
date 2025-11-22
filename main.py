import schedule
import time

from imcity_template import BaseBot, OrderBook, OrderRequest, Side
from src.fetch.main import fetch_schedule
from src.indicators.markets import price5, price6
from util import add_to_series

market5_estimate = None
market6_estimate = None

def calculate_expected_prices():
    arrivals = fetch_schedule(is_arrival=True)
    departures = fetch_schedule(is_arrival=False)

    global market5_estimate
    market5_estimate = price5(arrivals, departures)

    global market6_estimate
    market6_estimate = price6(arrivals, departures)

    print("New estimated price for market 5:", market5_estimate)
    print("New estimated price for market 6:", market6_estimate)

    if market5_estimate is not None and market6_estimate is not None:
        add_to_series(market5_estimate, market6_estimate)

print(20 * "-", "Script Started", 20 * "-")
# calculate_expected_prices()

# schedule.every(3).minutes.do(calculate_expected_prices)
print("Scheduler started. Press Ctrl+C to stop.")

class CustomBot(BaseBot):

    # Handler for own trades
    def on_trades(self, trades: list[dict]):
        for trade in trades:
            print(f"{trade['volume']} @ {trade['price']}")

    # Handler für Orderbuch-Updates
    def on_orderbook(self, orderbook: OrderBook):
        if orderbook.product == '5_Flights' and market5_estimate is not None:
            my_bid_price = market5_estimate * 0.9
            my_ask_price = market5_estimate * 1.1  

            print("Place buy at", my_bid_price, "and sell at", my_ask_price)

            self.send_order(OrderRequest(product=orderbook.product, 
                                     price=my_bid_price, 
                                     volume=1, 
                                     side=Side.BUY))
        
            self.send_order(OrderRequest(product=orderbook.product, 
                                        price=my_ask_price, 
                                        volume=1, 
                                        side=Side.SELL))
        elif orderbook.product == '6_Airport' and market6_estimate is not None:
            my_bid_price = market6_estimate * 0.9
            my_ask_price = market6_estimate * 1.1  

            print("Place buy at", my_bid_price, "and sell at", my_ask_price)

            self.send_order(OrderRequest(product=orderbook.product, 
                                     price=my_bid_price, 
                                     volume=1, 
                                     side=Side.BUY))
        
            self.send_order(OrderRequest(product=orderbook.product, 
                                        price=my_ask_price, 
                                        volume=1, 
                                        side=Side.SELL))

try:
    bot = CustomBot("http://ec2-52-31-108-187.eu-west-1.compute.amazonaws.com/", "Die Market-Macher eV.", "MarketMacherTUM!")
    bot.start()

    while True:
        #schedule.run_pending()
        time.sleep(1)

except KeyboardInterrupt:
    bot.stop()
    print("\nScript stopped.")