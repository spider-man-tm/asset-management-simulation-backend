"""
Main functions
"""

import math
import collections
from bisect import bisect_right
from typing import Optional

import numpy as np


class Asset:
    """ Asset class
    """

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
        no_tax: float
    ):
        self.name = name
        self.yld = yld / 100
        self.div = div / 100
        self.year = int(year)
        self.reserved = reserved
        self.init_fund = init_fund
        self.is_jp = bool(is_jp)
        self.volatility = volatility / 100
        self.no_tax = bool(no_tax)
        self.yld_month = (1 + self.yld) ** (1/12) - 1
        self.volatility_month = self.volatility * (1 / math.sqrt(12))
        self._capital_price_transition: Optional[list] = None
        self._price_transition: Optional[list] = None

    def __repr__(self):
        return f'Asset({self.__dict__})'

    @property
    def capital_price_transition(self):
        """ Return capital price transition (元本推移)
        """
        return self._capital_price_transition

    @property
    def price_transition(self):
        """ Return price transition (価格推移)
        """
        return self._price_transition

    def set_price_transition(self) -> None:
        """ Set the asset transition when operating for 20 years
        """
        capital_price_transition_month = [self.init_fund]
        price_transition_month = [self.init_fund]
        for year in range(20):   # max 20 years
            for month in range(12):
                if year < self.year:
                    capital_price_transition_month.append(
                        capital_price_transition_month[-1] + self.reserved)
                    price_transition_month.append(
                        price_transition_month[-1] *
                        (1 + self.yld_month) + self.reserved
                    )
                else:
                    capital_price_transition_month.append(
                        capital_price_transition_month[-1])
                    price_transition_month.append(
                        price_transition_month[-1] * (1 + self.yld_month)
                    )

        self._capital_price_transition = capital_price_transition_month[::12]
        self._price_transition = price_transition_month[::12]


def get_total_transion(assets: list[Asset]) -> dict:
    """ Returns the total price transition of all Assets

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
            capital_price_transition[i] += round(
                asset.capital_price_transition[i])
            original_price_transition[i] += round(asset.price_transition[i])
    return {
        'max_year': max_year,
        'priceTransition': original_price_transition,
        'capitalPriceTransition': capital_price_transition,
    }


def get_ratio_asset(assets: list[Asset]) -> dict:
    """ Returns the ratio of assets
    """
    max_year = max([asset.year for asset in assets])
    has_tax = []
    not_tax = []
    for asset in assets:
        not_tax.append(
            {'name': asset.name, 'y': asset.price_transition[max_year] // 10000})

        # NoTax(NISA)
        if asset.no_tax:
            has_tax.append(
                {'name': asset.name, 'y': asset.price_transition[max_year] // 10000})
        # HasTax
        else:
            profit = asset.price_transition[max_year] - \
                asset.capital_price_transition[max_year]
            tax = profit * 0.20315
            has_tax.append({
                'name': asset.name,
                'y': (asset.price_transition[max_year] - tax) // 10000
            })
    return {
        'notTax': not_tax,
        'hasTax': has_tax,
    }


def get_density_dist(assets: list[Asset], simulation_time: int = 1000) -> dict:
    """ Returns the density distribution of assets
    """
    # Returns an empty dictionary if the volatility of all assets is 0
    if all(asset.volatility_month == 0 for asset in assets):
        return {}

    max_year = max([asset.year for asset in assets])
    _result_total = np.zeros(simulation_time)
    table_rows = []
    for asset in assets:
        result = []
        _origin = asset.capital_price_transition[max_year]

        for _ in range(simulation_time):
            now_price = asset.init_fund
            random_norm = np.random.normal(
                loc=asset.yld_month, scale=asset.volatility_month, size=max_year*12)
            for year in range(max_year):
                for month in range(12):
                    if year < asset.year:
                        now_price = now_price * \
                            (1 + random_norm[year*month]) + asset.reserved
                    else:
                        now_price = now_price * (1 + random_norm[year*month])
            result.append(now_price - _origin)

        _result_total += np.array(result)

        _result = sorted(result)
        _idx = bisect_right(_result, 0)
        _prob = _idx / simulation_time * 100

        _top10 = _result[simulation_time // 10 * 9] // 10000
        _top30 = _result[simulation_time // 10 * 7] // 10000
        _worst30 = _result[simulation_time // 10 * 3] // 10000
        _worst10 = _result[simulation_time // 10] // 10000

        table_rows.append({
            'name': asset.name,
            'originPrice': _origin // 10000,
            'top10': f'+{_top10:.0f}' if _top10 > 0 else f'{_top10:.0f}' if _top10 < 0 else '±0',
            'top30': f'+{_top30:.0f}' if _top30 > 0 else f'{_top30:.0f}' if _top30 < 0 else '±0',
            'worst30': f'+{_worst30:.0f}' if _worst30 > 0 else f'{_worst30:.0f}' if _worst30 < 0 else '±0',
            'worst10': f'+{_worst10:.0f}' if _worst10 > 0 else f'{_worst10:.0f}' if _worst10 < 0 else '±0',
            'prob': f'{_prob:.2f} %'
        })

    result_total = list(_result_total)
    result_total = sorted(result_total)

    _min = result_total[0]
    _max = result_total[-1]
    _range = (_max - _min) // 10

    result_total = [r - _min for r in result_total]
    result_total = [r // _range * _range for r in result_total]
    result_total = [r - (_range // 2) + _min for r in result_total]
    result_total = [r // 10000 for r in result_total]

    cnt_result = collections.Counter(result_total).items()
    data = [[k, v / simulation_time] for k, v in cnt_result]

    return {'data': data, 'tableRows': table_rows}


def get_dividend_price(assets: list[Asset]) -> dict:
    """ Returns the total dividend price of all Assets
    """
    max_year = max([asset.year for asset in assets])
    prices = [0] * (max_year + 1)
    tax = [0] * (max_year + 1)
    for asset in assets:
        for i in range(max_year + 1):
            if i < len(asset.price_transition):
                p = asset.price_transition[i] * asset.div / 10000

                # NoTax(NISA)
                if asset.no_tax:
                    # JapanStock
                    if asset.is_jp:
                        prices[i] += p
                    # USStock
                    else:
                        p1 = p * 0.9
                        p2 = p - p1
                        prices[i] += p1
                        tax[i] += p2
                # HasTax
                else:
                    # JapanStock
                    if asset.is_jp:
                        p1 = p * 0.79685
                        p2 = p - p1
                        prices[i] += p1
                        tax[i] += p2
                    # USStock
                    else:
                        p1 = p * 0.71787
                        p2 = p - p1
                        prices[i] += p1
                        tax[i] += p2
            else:
                # NoTax(NISA)
                if asset.no_tax:
                    prices[i] += p
                # HasTax
                else:
                    prices[i] += p1
                    tax[i] += p2
    return {
        'price': [round(p, 1) for p in prices],
        'tax': [round(p, 1) for p in tax],
    }


def get_demolition_price(assets: list[Asset], duration: int) -> dict:
    """ Returns the total demolition price of all Assets
    """
    last_year = max([asset.year for asset in assets])
    price_transition = [0] * (duration + 1)

    demolition_per_year_total = 0

    for asset in assets:
        start_price = asset.price_transition[last_year]

        # NoTax(NISA)
        if asset.no_tax:
            # JapanStock
            if asset.is_jp:
                yield_year = asset.yld + asset.div
            # USStock
            else:
                yield_year = asset.yld + asset.div * 0.9
        # HasTax
        else:
            # JapanStock
            if asset.is_jp:
                yield_year = asset.yld + asset.div * 0.79685
            # USStock
            else:
                yield_year = asset.yld + asset.div * 0.71787

        k = (yield_year * (1 + yield_year)**duration) / \
            ((1 + yield_year)**duration - 1)

        demolition_per_year = start_price * k
        demolition_per_year_total += demolition_per_year

        for i in range(duration + 1):
            # i: year
            if i == 0:
                now_price = start_price
            else:
                now_price = now_price * (1 + yield_year) - demolition_per_year
            price_transition[i] += now_price // 10000
    price_transition[-1] = 0

    return {
        'duration': duration,
        'demolitionPrice': demolition_per_year_total // 10000,
        'priceTransition': price_transition,
    }
