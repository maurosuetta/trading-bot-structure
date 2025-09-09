from dataclasses import dataclass

@dataclass #SEARCH IF POSSIBLE TO MAKE SOME ATTRIBUTES PRIVATE, HOWEVER, IS PYTHON...
class Trade:
    timestamp: str
    type: str
    asset: str
    quantity: float
    entry_price: float
    stop_loss: float = 0.02
    take_profit: float = 0.04
    is_open: bool = False

    def cost_trade(self): #AREA IMPROVEMENT -> ADD COMISSION MARKET MAKER
        return self.quantity * self.entry_price
    
    def close_trade(self):
        self.is_open = False
    
    def open_trade(self):
        self.is_open = True
    
    #fix function
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