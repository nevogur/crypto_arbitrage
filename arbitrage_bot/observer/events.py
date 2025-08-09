from dataclasses import dataclass



"""
class PriceRecived is the data type created when a request to recive a price of a coin from the api is seccsecful
it is created by the exchanges files
the subscribers to PriceRecived are all the strategies
"""
@dataclass
class PriceRecived:
    time_stamp: float
    exchange: str
    coin: str
    ask: float
    bid: float
    
    
"""
class PosslibleArbitrage 

"""
@dataclass 
class PossibleArbitrage:
    pass
