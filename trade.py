from dataclasses import dataclass

@dataclass #SEARCH IF POSSIBLE TO MAKE SOME ATTRIBUTES PRIVATE, HOWEVER, IS PYTHON...
class Trade:
    timestamp: str
    type: str
    asset: str
    quantity: float
    entry_price: float
    stop_loss: float = 0.04
    take_profit: float = 0.08
    is_open: bool = False

    def cost_trade(self): #AREA IMPROVEMENT -> ADD COMISSION MARKET MAKER
        return self.quantity * self.entry_price
    
    def close_trade(self):
        self.is_open = False
    
    def open_trade(self):
        self.is_open = True
    
