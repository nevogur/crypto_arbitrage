from dataclasses import dataclass , field
from typing import Any , List , Dict , Optional
from decimal import Decimal
from strategies.abstract_arbitrage import AbstractArbitrage
from __future__ import annotations
from uuid import UUID, uuid4
import time



"""
class PriceRecived is the data type created when a request to recive a price of a symbol from the api is seccsecful
it is created by the exchanges files
the subscribers to PriceRecived are all the strategies

@params
    time_stamp: float - the time of the recived price: unix
    exchange: str - the name of the exchange the data is from
    symbol: str - the name of the symbol the data is about 
    ask: float - the asking price for the symbol
    bid: float - the bidding price for the symbol
    correlation_id: UUID - an ID to be able to track what class was created and where

***Emitted by exchange feed(s) when a fresh top-of-book quote is available
"""
@dataclass(frozen=True)
class PriceRecived:
    time_stamp: float = field(default_factory=time.time)
    exchange: str
    symbol: str
    ask: float
    bid: float
    correlation_id: UUID = field(default_factory=uuid4)

    



"""
class OrderLeg is one part of the arbitrage includes what symbol to buy, from what exchange and at what price
it is created from the strategies
since it is one part of the arbitrage no one sees this class on it's own only has a "TradePlan"

@params 
    exchange: str - name of exchange to buy from: "binance"
    symbol: str - name of symbol to buy: "BTC/ETH"
    side: str - should you buy of sell: "BUY" or "SELL"
    amount: Decimal - how much to buy: 0.01
    price_limit : Optional[Decimal] = None - should there be a limit to the buy price None means "Market" price
    
***One executable order leg
"""
@dataclass(frozen=True)
class OrderLeg:
    exchange: str
    symbol: str
    side: str
    amount: Decimal 
    price_limit : Optional[Decimal] = None
  
  
"""
class TradePlan contains all the trades that need to be done in an arbitrage
it is created by the strategy

@params 
    trades: List[OrderLeg] - a list of all the OrderLegs that need to happen for an arbitrage
    expected_profit_precentage: Decimal - the expected profit of the arbitrage in a precentage after fees and taxes: 0.03
    
***A set of legs that together implement an arbitrage cycle
""" 
@dataclass(frozen=True)
class TradePlan:
    trades: List[OrderLeg]
    expected_profit_precentage: Decimal
    


    
"""
class PosslibleArbitrage is created when a certain strategy finds an arbitrage 
is it created in the startegies files
the subscribes to PossibleArbitrage are the risk analysis files

@params
    strategy: AbstractArbitrage - the arbitrage strategy the found the arbitrage: "Triangular"
    plan: the Tradeplan
    time_stamp: float - the exact time the object was created: unix
    correlation_id: UUID - an ID to be able to track what class was created and where

***Emitted by a strategy when it detects a candidate trade
"""
@dataclass(frozen=True)
class PossibleArbitrage:
    
    strategy: AbstractArbitrage
    plan: TradePlan
    time_stamp: float = field(default_factory=time.time)
    correlation_id: UUID = field(default_factory=uuid4)




"""
class ConfirmedArbitrage is created when an arbitrage went through all the risk analysis and was found safe to exacute
it is created in the risk files
the subscribers to ConfirmedArbitrage are the execution files

@params
    plan: the Tradeplan
    time_stamp: float - the exact time the object was created: unix
    correlation_id: UUID - an ID to be able to track what class was created and where
        
***Emitted by Risk when the candidate passes checks; may include an adjusted plan
"""

@dataclass(frozen=True)
class ConfirmedArbitrage:


    plan: TradePlan
    time_stamp: float = field(default_factory=time.time)
    correlation_id: UUID = field(default_factory=uuid4)



"""
@params
    time_stamp: float - the exact time the object was created: unix
    correlation_id: UUID - an ID to be able to track what class was created and where
    reason: str - the reason the arbitrage fails: 'slippage', 'size', 'cooldown'
    details: Optional[str] = None - full explaination if exists

***Emitted by Risk when a candidate fails checks (documentation + observability).
"""
@dataclass(frozen=True)
class RejectedArbitrage:
    time_stamp: float = field(default_factory=time.time)
    correlation_id: UUID = field(default_factory=uuid4)
    reason: str                            
    details: Optional[str] = None     


"""
Emitted by Execution after an order leg is attempted (paper or live).
Carries the planned leg and realized execution details.
"""
@dataclass(frozen=True)
class FillEvent:
    pass
    


"""
class DoneArbitrage is created when an arbitrage has been executed

"""
@dataclass(frozen=True)
class DoneArbitrage:
    pass