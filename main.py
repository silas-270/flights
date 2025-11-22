import schedule
import logging

# --- 1. Setup Logging Configuration ---
logging.basicConfig(
    level=logging.INFO,  # Change to logging.DEBUG to see "No Action" logs
    format='%(asctime)s | %(levelname)-8s | %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger("TradingBot")

from imcity_template import BaseBot, OrderBook, OrderRequest, Side
from src.fetch.main import fetch_schedule
from src.indicators.markets import price5, price6

def calculate_expected_prices():
    try:
        arrivals = fetch_schedule(is_arrival=True)
        departures = fetch_schedule(is_arrival=False)

        global m5_fair_value
        m5_fair_value = price5(arrivals, departures)

        global m6_fair_value
        m6_fair_value = price6(arrivals, departures)

        # Clear visual separator for price updates
        logger.info(f"{'-'*15} PRICE UPDATE {'-'*15}")
        logger.info(f"Est M5 (Flights): {m5_fair_value}")
        logger.info(f"Est M6 (Airport): {m6_fair_value}")

    except Exception as e:
        logger.error(f"Error calculating prices: {e}")

class CustomBot(BaseBot):

    def on_trades(self, trades: list[dict]):
        return

    def on_orderbook(self, orderbook: OrderBook):
        product = orderbook.product
        if not product == '5_Flights' and not product == '6_Airports':
            return
        fair_value = m5_fair_value if product == '5_Flights' else m6_fair_value

        if not orderbook.buy_orders or not orderbook.sell_orders:
            return

        best_bid = orderbook.buy_orders[0]
        best_ask = orderbook.sell_orders[0]

        if best_bid.price >= best_ask.price:
            return

        spread = 0.008
        mid = (best_bid.price + best_ask.price) / 2
        mean_price = (mid + fair_value) / 2

        # Clear old Orders before making new ones
        self.clear_orders_for_product(product)

        # Open new Orders
        price = round(mean_price * ((1 + spread) if fair_value > mean_price else (1 - spread)))
        order = OrderRequest(product=orderbook.product,
                             price=price,
                             volume=1,
                             side=(Side.BUY if fair_value > mean_price else Side.SELL)
                             )
        
        print(f"Fair: {fair_value}, Mean: {mean_price} -> {"Buy" if fair_value > mean_price else "Sell"} at {price}")
            
        self.send_order(order)

m5_fair_value = None 
m6_fair_value = None

try:
    print("\n")
    logger.info(f"{'='*10} BOT INITIALIZATION {'='*10}")
    
    calculate_expected_prices()
    schedule.every(3).minutes.do(calculate_expected_prices)
    
    logger.info("Scheduler started.")

    market_bot = CustomBot("http://ec2-18-203-201-148.eu-west-1.compute.amazonaws.com", "Die Market-Macher eV.", "MarketMacherTUM!")
    market_bot.start()

    logger.info("Bot connected. Monitoring streams...")
    
    while True:
        schedule.run_pending()
        pass

except KeyboardInterrupt:
    market_bot.stop()
    print("\n")
    logger.info("🛑 Script stopped by user.")