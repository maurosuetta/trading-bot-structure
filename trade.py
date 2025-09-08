from dataclasses import dataclass
from portfolio import Portfolio

@dataclass
class Trade:
    timestamp: str
    type: str
    asset: str
    quantity: float
    entry_price: float
    stop_loss: float
    take_profit: float
    is_open: bool = True

    def close_trade(self):
        self.is_open = False
    
    def check_stoploss_takeprofit(self, current_prices, current_time, portfolio):

        for asset in current_prices:
            if self.take_profit <= ( (current_prices[asset]-self.entry_price) / self.entry_price):
                print(f"[{current_time}] Take Profit Activated {self.take_profit}%")
                self.close_trade()
                portfolio.calculate_equity(current_prices, current_time)

            elif self.stop_loss <= -( (current_prices[asset]-self.entry_price) / self.entry_price):
                print(f"[{current_time}] Stop Loss Activated {self.take_profit}%")
                self.close_trade()
                portfolio.calculate_equity(current_prices, current_time)
            else:
                pass
# The equity calculation (portfolio.calculate_equity(...)) might be better handled at the portfolio level, after trades are closed, to keep responsibilities separated.
# You may want to record the closing transaction (price, time, reason) for history/reporting.
# If you have multiple assets, make sure each trade only checks its own asset.