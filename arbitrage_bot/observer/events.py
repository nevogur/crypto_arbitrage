from __future__ import annotations
from dataclasses import dataclass , field
from typing import Any , List , Dict , Optional
from decimal import Decimal
from uuid import UUID, uuid4
import time


    
"""
class PriceReceived is the data type created when a request to recive a price of a symbol from the api is seccsecful
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
class PriceReceived:
    exchange: str
    symbol: str
    ask: Decimal = Decimal("0")
    bid: Decimal = Decimal("0")
    time_stamp: float = field(default_factory=time.time)
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
    amount: Decimal = Decimal("0")
    price_limit : Optional[Decimal] = None
  
  
"""
class TradePlan contains all the trades that need to be done in an arbitrage
it is created by the strategy

@params 
    trades: List[OrderLeg] - a list of all the OrderLegs that need to happen for an arbitrage
    expected_profit_percentage: Decimal - the expected profit of the arbitrage in a precentage after fees and taxes: 0.03
    
***A set of legs that together implement an arbitrage cycle
""" 
@dataclass(frozen=True)
class TradePlan:
    trades: List[OrderLeg]
    expected_profit_percentage: Decimal = Decimal("0")
    


    
"""
class PosslibleArbitrage is created when a certain strategy finds an arbitrage 
is it created in the startegies files
the subscribes to PossibleArbitrage are the risk analysis files

@params
    strategy: str - the arbitrage strategy the found the arbitrage: "Triangular"
    plan: the Tradeplan
    time_stamp: float - the exact time the object was created: unix
    correlation_id: UUID - an ID to be able to track what class was created and where

***Emitted by a strategy when it detects a candidate trade
"""
@dataclass(frozen=True)
class PossibleArbitrage: 
    strategy: str
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
    reason: str                            
    details: Optional[str] = None 
    time_stamp: float = field(default_factory=time.time)
    correlation_id: UUID = field(default_factory=uuid4)    


"""
class FillEvent is created when an order is placed by the execution files

@params
   order: OrderLeg -The original planned trade details (exchange, symbol, side, amount, etc.).
    time_stamp: float - UNIX timestamp when the fill was recorded (auto-filled to creation time).
    correlation_id: UUID
        Unique ID tying all related events for the same arbitrage cycle.
        Usually inherited from the strategy's PossibleArbitrage event.
        
    price_paid: Decimal - Average fill price for the leg (can differ from intended price due to slippage).
    fees: Decimal - Total fees charged for this leg (in quote currency, e.g., USDT).
    status: str - Execution outcome for the leg: "filled", "partial", "canceled", "rejected".
    filled_amount: Decimal -How much of the intended amount was actually filled (important for partial fills).

Emitted by Execution after an order leg is attempted (paper or live).
Carries the planned leg and realized execution details.
"""
@dataclass(frozen=True)
class FillEvent:
    order: OrderLeg
    status: str
    price_paid: Decimal = Decimal("0")
    fees: Decimal = Decimal("0")
    filled_amount: Decimal = Decimal("0")
    time_stamp: float = field(default_factory=time.time)
    correlation_id: UUID = field(default_factory=uuid4)
    
    


"""
class DoneArbitrage is created when an arbitrage has been executed.
Its purpose is to log the complete outcome of all the executed trades in an arbitrage cycle,
including financial results and execution success.

@params
    trades: List[FillEvent]
        The list of FillEvent objects representing each executed leg of the arbitrage plan.
        Each FillEvent contains the actual execution details for its corresponding OrderLeg.
    
    success: bool
        Overall execution outcome for the arbitrage cycle.
        True if all legs were fully filled ("filled" status), False otherwise.
    
    notes: Optional[str]
        Optional human-readable notes about the arbitrage execution.
        Can contain diagnostic information, error messages, or metadata for logging.

    real_gain: Decimal
        Realized profit or loss from the arbitrage in quote currency, after deducting fees.
        Calculated from the difference between proceeds from sell legs and costs of buy legs.
    
    total_fees: Decimal
        Total combined fees from all executed legs in quote currency.

    total_tax: Decimal
        Total tax liability computed on profitable trades.
        Will be zero if the arbitrage was unprofitable or if tax calculation is disabled.
    
    time_stamp: float
        UNIX timestamp of when this DoneArbitrage event object was created.

    correlation_id: UUID
        Unique ID tying all related events for the same arbitrage cycle.
        Usually inherited from the originating PossibleArbitrage event for traceability.

Methods:
    get_real_pnl(trades: List[FillEvent]) -> Decimal
        Static method to compute realized profit or loss from a set of FillEvent trades.
    
    data_from_trades(cls, trades: List[FillEvent], notes: Optional[str] = None, tax_rate: Decimal = Decimal("0.25")) -> DoneArbitrage
        Class method that builds a DoneArbitrage instance from a set of FillEvent trades.
        Automatically calculates total fees, profit/loss, tax liability, and sets the success flag.

Emitted by:
    Execution after all planned legs for a confirmed arbitrage have been attempted
    (in paper or live mode). Provides the final consolidated record of the trade cycle.
"""
@dataclass(frozen=True)
class DoneArbitrage:
    trades: List[FillEvent]
    success: bool 
    notes: Optional[str] = None
    real_gain: Decimal = Decimal("0")
    total_fees: Decimal = Decimal("0")
    total_tax: Decimal = Decimal("0")
    time_stamp: float = field(default_factory=time.time)
    correlation_id: UUID = field(default_factory=uuid4)

    @staticmethod       
    def get_real_pnl(trades: List[FillEvent]) -> Decimal:
        cost = Decimal("0")
        proceeds = Decimal("0")
        for trade in trades:
            if(trade.order.side == "BUY"):
                cost += trade.price_paid * trade.filled_amount + trade.fees
            else:
                proceeds += trade.price_paid * trade.filled_amount - trade.fees
        return proceeds - cost
    
 
    @classmethod
    def data_from_trades(cls , trades: List[FillEvent] , notes: Optional[str] = None , tax_rate = Decimal("0.25")) -> DoneArbitrage:
        time_stamp = time.time()
        correlation_id = uuid4()
        total_fees = Decimal("0")
        total_tax = Decimal("0")
        success = True
        real_gain = cls.get_real_pnl(trades)
        if(real_gain > 0):
            total_tax = real_gain * tax_rate
        for event in trades:
            total_fees += event.fees
            if(event.status.lower() != "filled"):
                success = False
        
        return cls(trades= trades , success= success , 
                             notes= notes , real_gain= real_gain ,
                             total_fees= total_fees , total_tax= total_tax , 
                             time_stamp= time_stamp , correlation_id= correlation_id)
        



    