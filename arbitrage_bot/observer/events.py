from dataclasses import dataclass
from typing import Any , List , Dict
from strategies.abstract_arbitrage import AbstractArbitrage



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
class PosslibleArbitrage is created when a certain strategy finds an arbitrage 
is it created in the startegies files
the subscribes to PossibleArbitrage are the risk analysis files

"""
@dataclass 
class PossibleArbitrage:
    strategy: AbstractArbitrage
    exchanges: List[str]
    coins: Dict[float]
    time_stamp: float



"""
class ConfirmedArbitrage is created when an arbitrage went through all the risk analysis and was found safe to exacute
it is created in the risk files
the subscribers to ConfirmedArbitrage are the execution files
    
"""

@dataclass
class ConfirmedArbitrage:
    pass



"""
class DoneArbitrage is created when an arbitrage has been executed

"""
@dataclass
class DoneArbitrage:
    pass