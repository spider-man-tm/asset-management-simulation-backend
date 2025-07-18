"""
Test cases for asset_calc.py
"""

import pytest

from src.asset_calc import (
    Asset,
    get_demolition_price,
    get_dividend_price,
    get_ratio_asset,
    get_total_transition,
)


@pytest.fixture
def asset1():
    asset = Asset('三菱UFJ', 3.3, 4.1, 8, 5000, 300000, 1, 3.2, 1)
    asset.set_price_transition()
    return asset


@pytest.fixture
def asset2():
    asset = Asset('APPL', 8, 1.8, 11, 5200, 200000, 0, 4.5, 1)
    asset.set_price_transition()
    return asset


@pytest.fixture
def asset3():
    asset = Asset('伊藤忠商事', 5.5, 3.2, 9, 5000, 100, 1, 2.3, 0)
    asset.set_price_transition()
    return asset


@pytest.fixture
def asset4():
    asset = Asset('GOOGL', 11.3, 0.2, 10, 5500, 0, 0, 5.2, 0)
    asset.set_price_transition()
    return asset


def test__capital_price_transition(asset1, asset2, asset3, asset4):
    asset1_tran = [
        300000.0,
        360000.0,
        420000.0,
        480000.0,
        540000.0,
        600000.0,
        660000.0,
        720000.0,
        780000.0,
        780000.0,
        780000.0,
        780000.0,
        780000.0,
        780000.0,
        780000.0,
        780000.0,
        780000.0,
        780000.0,
        780000.0,
        780000.0,
        780000.0,
    ]
    asset2_tran = [
        200000.0,
        262400.0,
        324800.0,
        387200.0,
        449600.0,
        512000.0,
        574400.0,
        636800.0,
        699200.0,
        761600.0,
        824000.0,
        886400.0,
        886400.0,
        886400.0,
        886400.0,
        886400.0,
        886400.0,
        886400.0,
        886400.0,
        886400.0,
        886400.0,
    ]
    asset3_tran = [
        100.0,
        60100.0,
        120100.0,
        180100.0,
        240100.0,
        300100.0,
        360100.0,
        420100.0,
        480100.0,
        540100.0,
        540100.0,
        540100.0,
        540100.0,
        540100.0,
        540100.0,
        540100.0,
        540100.0,
        540100.0,
        540100.0,
        540100.0,
        540100.0,
    ]
    asset4_tran = [
        0.0,
        66000.0,
        132000.0,
        198000.0,
        264000.0,
        330000.0,
        396000.0,
        462000.0,
        528000.0,
        594000.0,
        660000.0,
        660000.0,
        660000.0,
        660000.0,
        660000.0,
        660000.0,
        660000.0,
        660000.0,
        660000.0,
        660000.0,
        660000.0,
    ]
    assert asset1.capital_price_transition == asset1_tran
    assert asset2.capital_price_transition == asset2_tran
    assert asset3.capital_price_transition == asset3_tran
    assert asset4.capital_price_transition == asset4_tran


def test__price_transition(asset1, asset2, asset3, asset4):
    asset1_tran = [
        300000.0,
        370802.18020972534,
        443940.83236637147,
        519493.06004418683,
        597538.51123537,
        678159.4623158621,
        761440.9047820102,
        847470.634849541,
        936339.3460093006,
        967238.5444276062,
        999157.4163937158,
        1032129.6111347071,
        1066189.8883021506,
        1101374.1546161207,
        1137719.501718451,
        1175264.2452751582,
        1214047.965369237,
        1254111.54822642,
        1295497.2293178902,
        1338248.6378853791,
        1382410.842935595,
    ]
    asset2_tran = [
        200000.0,
        280656.20969867916,
        367764.9161732527,
        461842.31916579214,
        563445.9143977346,
        673177.7972482325,
        791688.2307267701,
        919679.4988835909,
        1057910.0684929574,
        1207199.0836710727,
        1368431.2200634372,
        1542561.9273671915,
        1665966.8815565663,
        1799244.2320810913,
        1943183.770647578,
        2098638.472299383,
        2266529.550083333,
        2447851.9140899987,
        2643680.0672171973,
        2855174.472594572,
        3083588.4304021373,
    ]
    asset3_tran = [
        100.0,
        61603.379240458446,
        126489.44433914212,
        194944.24301825347,
        267164.0556247158,
        343355.95792453375,
        423738.41485084157,
        508541.90690809634,
        598009.5910285,
        692397.997775526,
        730479.88765318,
        770656.2814741048,
        813042.3769551808,
        857759.7076877158,
        904936.4916105402,
        954707.9986491201,
        1007216.9385748217,
        1062613.870196437,
        1121057.633057241,
        1182715.8028753896,
        1247765.1720335365,
    ]
    asset4_tran = [
        0.0,
        69352.18755690311,
        146541.17230773615,
        232452.51233541325,
        328071.8337862177,
        434496.13856096304,
        552946.3897752545,
        684781.5193767607,
        831514.0186232369,
        994827.2902845647,
        1176594.9616436223,
        1309550.19230935,
        1457529.3640403047,
        1622230.182176857,
        1805542.1927628398,
        2009568.4605450386,
        2236649.6965866247,
        2489391.1123009096,
        2770692.307990909,
        3083780.5387938786,
        3432247.7396775824,
    ]
    assert asset1.price_transition == asset1_tran
    assert asset2.price_transition == asset2_tran
    assert asset3.price_transition == asset3_tran
    assert asset4.price_transition == asset4_tran


def test__get_total_transition(asset1, asset2, asset3, asset4):
    expected = {
        'max_year': 11,
        'capitalPriceTransition': [
            500100,
            748500,
            996900,
            1245300,
            1493700,
            1742100,
            1990500,
            2238900,
            2487300,
            2675700,
            2804100,
            2866500,
        ],
        'priceTransition': [
            500100,
            782413,
            1084736,
            1408732,
            1756221,
            2129189,
            2529813,
            2960474,
            3423773,
            3861663,
            4274663,
            4654898,
        ],
    }
    assert get_total_transition([asset1, asset2, asset3, asset4]) == expected


def test__get_ratio_asset(asset1, asset2, asset3, asset4):
    expected = {
        'hasTax': [
            {'name': '三菱UFJ', 'y': 103.0},
            {'name': 'APPL', 'y': 154.0},
            {'name': '伊藤忠商事', 'y': 72.0},
            {'name': 'GOOGL', 'y': 117.0},
        ],
        'notTax': [
            {'name': '三菱UFJ', 'y': 103.0},
            {'name': 'APPL', 'y': 154.0},
            {'name': '伊藤忠商事', 'y': 77.0},
            {'name': 'GOOGL', 'y': 130.0},
        ],
    }
    assert get_ratio_asset([asset1, asset2, asset3, asset4]) == expected


def test__get_dividend_price(asset1, asset2, asset3, asset4):
    expected = {
        'price': [1.6, 2.1, 2.8, 3.4, 4.1, 4.8, 5.6, 6.4, 7.2, 7.8, 8.3, 8.9],
        'tax': [0.0, 0.1, 0.2, 0.2, 0.3, 0.4, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9],
    }
    assert get_dividend_price([asset1, asset2, asset3, asset4]) == expected


def test__get_demolition_price(asset1, asset2, asset3, asset4):
    expected = {
        'demolitionPrice': 52.0,
        'duration': 20,
        'priceTransition': [
            464.0,
            455.0,
            445.0,
            434.0,
            423.0,
            411.0,
            396.0,
            382.0,
            366.0,
            347.0,
            328.0,
            308.0,
            284.0,
            258.0,
            230.0,
            199.0,
            167.0,
            131.0,
            90.0,
            47.0,
            0,
        ],
    }
    assert (
        get_demolition_price([asset1, asset2, asset3, asset4], duration=20) == expected
    )
