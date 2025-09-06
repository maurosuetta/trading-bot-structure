class Strategy:

    def __init__(self, asset_symbol='str'):
        self.asset_symbol = asset_symbol
        self.parameters = {}

    def set_parameters(self, **params):
        self.parameters.update(params)
        print(f"Strategy: {self.strategy_name} -> parameters set for {self.asset_symbol}: {self.parameters}")

    def generate_signals(self, data) -> str:
        #this method must be overriden by the subclass
        raise NotImplementedError("The generate_signals() method must be implemented by a subclass.")
   