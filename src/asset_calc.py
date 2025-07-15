"""
Main functions
"""

import collections
import math
from bisect import bisect_right
from typing import Optional

import numpy as np


class Constants:
    """Constants used in asset calculations"""

    # Percentage conversion
    PERCENT_TO_DECIMAL = 100

    # Time constants
    MONTHS_IN_YEAR = 12
    MAX_YEARS = 20

    # Tax rates
    CAPITAL_GAINS_TAX_RATE = 0.20315  # Japan capital gains tax rate
    US_WITHHOLDING_TAX_NISA = 0.9  # US stocks in NISA (after 10% withholding)
    JP_DIVIDEND_TAX_TAXABLE = 0.79685  # Japan dividend after tax in taxable account
    US_DIVIDEND_TAX_TAXABLE = 0.71787  # US dividend after tax in taxable account

    # Display constants
    YEN_UNIT_DIVISOR = 10000  # Convert to 万円 (10,000 yen units)

    # Simulation constants
    DEFAULT_SIMULATION_TIME = 1000
    PERCENTILE_DIVISOR = 10
    RANGE_DIVISOR = 2


class DividendTaxCalculator:
    """Dividend tax calculation utility for different asset types and account types"""

    @staticmethod
    def get_dividend_tax_rate(is_jp: bool, no_tax: bool) -> float:
        """Get dividend tax rate based on asset and account type

        Args:
            is_jp: True if Japanese stock, False if US stock
            no_tax: True if NISA account, False if taxable account

        Returns:
            Tax rate (multiplier for net amount after tax)
        """
        if no_tax:  # NISA account
            if is_jp:
                return 1.0  # No tax for Japanese stocks in NISA
            else:
                return Constants.US_WITHHOLDING_TAX_NISA  # US withholding tax only
        else:  # Taxable account
            if is_jp:
                return Constants.JP_DIVIDEND_TAX_TAXABLE  # Japan dividend tax
            else:
                return Constants.US_DIVIDEND_TAX_TAXABLE  # US withholding + Japan tax

    @staticmethod
    def calculate_dividend_after_tax(
        amount: float, is_jp: bool, no_tax: bool
    ) -> tuple[float, float]:
        """Calculate dividend amount after tax

        Args:
            amount: Original dividend amount
            is_jp: True if Japanese stock, False if US stock
            no_tax: True if NISA account, False if taxable account

        Returns:
            Tuple of (net_amount, tax_amount)
        """
        tax_rate = DividendTaxCalculator.get_dividend_tax_rate(is_jp, no_tax)
        net_amount = amount * tax_rate
        tax_amount = amount - net_amount
        return net_amount, tax_amount

    @staticmethod
    def get_yield_after_tax(dividend_yield: float, is_jp: bool, no_tax: bool) -> float:
        """Get effective dividend yield after tax

        Args:
            dividend_yield: Original dividend yield
            is_jp: True if Japanese stock, False if US stock
            no_tax: True if NISA account, False if taxable account

        Returns:
            Effective dividend yield after tax
        """
        tax_rate = DividendTaxCalculator.get_dividend_tax_rate(is_jp, no_tax)
        return dividend_yield * tax_rate


class Asset:
    """Asset class"""

    def __init__(
        self,
        name: str,
        yld: float,
        div: float,
        year: float,
        reserved: float,
        init_fund: float,
        is_jp: float,
        volatility: float,
        no_tax: float,
    ):
        self.name = name
        self.yld = yld / Constants.PERCENT_TO_DECIMAL
        self.div = div / Constants.PERCENT_TO_DECIMAL
        self.year = int(year)
        self.reserved = reserved
        self.init_fund = init_fund
        self.is_jp = bool(is_jp)
        self.volatility = volatility / Constants.PERCENT_TO_DECIMAL
        self.no_tax = bool(no_tax)
        self.yld_month = (1 + self.yld) ** (1 / Constants.MONTHS_IN_YEAR) - 1
        self.volatility_month = self.volatility * (
            1 / math.sqrt(Constants.MONTHS_IN_YEAR)
        )
        self._capital_price_transition: Optional[list] = None
        self._price_transition: Optional[list] = None

    def __repr__(self):
        return f'Asset({self.__dict__})'

    @property
    def capital_price_transition(self):
        """Return capital price transition (元本推移)"""
        return self._capital_price_transition

    @property
    def price_transition(self):
        """Return price transition (価格推移)"""
        return self._price_transition

    def set_price_transition(self) -> None:
        f"""Set the asset transition when operating for {Constants.MAX_YEARS} years"""
        capital_price_transition_month = [self.init_fund]
        price_transition_month = [self.init_fund]
        for year in range(Constants.MAX_YEARS):
            for month in range(Constants.MONTHS_IN_YEAR):
                if year < self.year:
                    capital_price_transition_month.append(
                        capital_price_transition_month[-1] + self.reserved
                    )
                    price_transition_month.append(
                        price_transition_month[-1] * (1 + self.yld_month)
                        + self.reserved
                    )
                else:
                    capital_price_transition_month.append(
                        capital_price_transition_month[-1]
                    )
                    price_transition_month.append(
                        price_transition_month[-1] * (1 + self.yld_month)
                    )

        self._capital_price_transition = capital_price_transition_month[
            :: Constants.MONTHS_IN_YEAR
        ]
        self._price_transition = price_transition_month[:: Constants.MONTHS_IN_YEAR]


def get_total_transition(assets: list[Asset]) -> dict:
    """Returns the total price transition of all Assets

    Args:
        assets (list[Asset]): List of Asset objects
    Returns:
        dict: Total price transition of all Assets
    """
    max_year = max([asset.year for asset in assets])
    capital_price_transition = [0] * (max_year + 1)
    original_price_transition = [0] * (max_year + 1)
    for asset in assets:
        for i in range(max_year + 1):
            # i: year
            capital_price_transition[i] += round(asset.capital_price_transition[i])
            original_price_transition[i] += round(asset.price_transition[i])
    return {
        'max_year': max_year,
        'priceTransition': original_price_transition,
        'capitalPriceTransition': capital_price_transition,
    }


def get_ratio_asset(assets: list[Asset]) -> dict:
    """Returns the ratio of assets"""
    max_year = max([asset.year for asset in assets])
    has_tax = []
    not_tax = []
    for asset in assets:
        not_tax.append(
            {
                'name': asset.name,
                'y': asset.price_transition[max_year] // Constants.YEN_UNIT_DIVISOR,
            }
        )

        # NoTax(NISA)
        if asset.no_tax:
            has_tax.append(
                {
                    'name': asset.name,
                    'y': asset.price_transition[max_year] // Constants.YEN_UNIT_DIVISOR,
                }
            )
        # HasTax
        else:
            profit = (
                asset.price_transition[max_year]
                - asset.capital_price_transition[max_year]
            )
            tax = profit * Constants.CAPITAL_GAINS_TAX_RATE
            has_tax.append(
                {
                    'name': asset.name,
                    'y': (asset.price_transition[max_year] - tax)
                    // Constants.YEN_UNIT_DIVISOR,
                }
            )
    return {
        'notTax': not_tax,
        'hasTax': has_tax,
    }


def get_density_dist(
    assets: list[Asset], simulation_time: int = Constants.DEFAULT_SIMULATION_TIME
) -> dict:
    """Returns the density distribution of assets"""
    max_year = max([asset.year for asset in assets])
    _result_total = np.zeros(simulation_time)
    table_rows = []
    for asset in assets:
        result = []
        _origin = asset.capital_price_transition[max_year]

        for _ in range(simulation_time):
            now_price = asset.init_fund
            random_norm = np.random.normal(
                loc=asset.yld_month,
                scale=asset.volatility_month,
                size=max_year * Constants.MONTHS_IN_YEAR,
            )
            for year in range(max_year):
                for month in range(Constants.MONTHS_IN_YEAR):
                    if year < asset.year:
                        now_price = (
                            now_price
                            * (1 + random_norm[year * Constants.MONTHS_IN_YEAR + month])
                            + asset.reserved
                        )
                    else:
                        now_price = now_price * (
                            1 + random_norm[year * Constants.MONTHS_IN_YEAR + month]
                        )
            result.append(now_price - _origin)

        _result_total += np.array(result)

        _result = sorted(result)
        _idx = bisect_right(_result, 0)
        _prob = _idx / simulation_time * Constants.PERCENT_TO_DECIMAL

        _top10 = (
            _result[simulation_time // Constants.PERCENTILE_DIVISOR * 9]
            // Constants.YEN_UNIT_DIVISOR
        )
        _top30 = (
            _result[simulation_time // Constants.PERCENTILE_DIVISOR * 7]
            // Constants.YEN_UNIT_DIVISOR
        )
        _worst30 = (
            _result[simulation_time // Constants.PERCENTILE_DIVISOR * 3]
            // Constants.YEN_UNIT_DIVISOR
        )
        _worst10 = (
            _result[simulation_time // Constants.PERCENTILE_DIVISOR]
            // Constants.YEN_UNIT_DIVISOR
        )

        table_rows.append(
            {
                'name': asset.name,
                'originPrice': _origin // Constants.YEN_UNIT_DIVISOR,
                'top10': (
                    f'+{_top10:.0f}'
                    if _top10 > 0
                    else f'{_top10:.0f}' if _top10 < 0 else '±0'
                ),
                'top30': (
                    f'+{_top30:.0f}'
                    if _top30 > 0
                    else f'{_top30:.0f}' if _top30 < 0 else '±0'
                ),
                'worst30': (
                    f'+{_worst30:.0f}'
                    if _worst30 > 0
                    else f'{_worst30:.0f}' if _worst30 < 0 else '±0'
                ),
                'worst10': (
                    f'+{_worst10:.0f}'
                    if _worst10 > 0
                    else f'{_worst10:.0f}' if _worst10 < 0 else '±0'
                ),
                'prob': f'{_prob:.2f} %',
            }
        )

    result_total = list(_result_total)
    result_total = sorted(result_total)

    _min = result_total[0]
    _max = result_total[-1]
    _range = (_max - _min) // Constants.PERCENTILE_DIVISOR

    result_total = [r - _min for r in result_total]
    result_total = [r // _range * _range for r in result_total]
    result_total = [
        r - (_range // Constants.RANGE_DIVISOR) + _min for r in result_total
    ]
    result_total = [r // Constants.YEN_UNIT_DIVISOR for r in result_total]

    cnt_result = collections.Counter(result_total).items()
    data = [[k, v / simulation_time] for k, v in cnt_result]

    return {'data': data, 'tableRows': table_rows}


def get_dividend_price(assets: list[Asset]) -> dict:
    """Returns the total dividend price of all Assets"""
    max_year = max([asset.year for asset in assets])
    prices = [0.0] * (max_year + 1)
    tax = [0.0] * (max_year + 1)
    for asset in assets:
        for i in range(max_year + 1):
            if i < len(asset.price_transition):
                p = asset.price_transition[i] * asset.div / Constants.YEN_UNIT_DIVISOR

                p1, p2 = DividendTaxCalculator.calculate_dividend_after_tax(
                    p, asset.is_jp, asset.no_tax
                )
                prices[i] += p1
                tax[i] += p2
            else:
                # Use the last calculated p1, p2 values
                prices[i] += p1
                tax[i] += p2
    return {
        'price': [round(p, 1) for p in prices],
        'tax': [round(p, 1) for p in tax],
    }


def get_demolition_price(assets: list[Asset], duration: int) -> dict:
    """Returns the total demolition price of all Assets"""
    last_year = max([asset.year for asset in assets])
    price_transition = [0] * (duration + 1)

    demolition_per_year_total = 0

    for asset in assets:
        start_price = asset.price_transition[last_year]

        effective_dividend_yield = DividendTaxCalculator.get_yield_after_tax(
            asset.div, asset.is_jp, asset.no_tax
        )
        yield_year = asset.yld + effective_dividend_yield

        k = (yield_year * (1 + yield_year) ** duration) / (
            (1 + yield_year) ** duration - 1
        )

        demolition_per_year = start_price * k
        demolition_per_year_total += demolition_per_year

        for i in range(duration + 1):
            # i: year
            if i == 0:
                now_price = start_price
            else:
                now_price = now_price * (1 + yield_year) - demolition_per_year
            price_transition[i] += now_price // Constants.YEN_UNIT_DIVISOR
    price_transition[-1] = 0

    return {
        'duration': duration,
        'demolitionPrice': demolition_per_year_total // Constants.YEN_UNIT_DIVISOR,
        'priceTransition': price_transition,
    }
