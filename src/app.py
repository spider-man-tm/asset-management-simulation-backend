"""
Flask App main modules
"""

import os
import urllib.parse

from flask import Flask, request, jsonify
from flask_cors import CORS

from utils import set_seed
from asset_calc import (
    Asset,
    get_total_transion,
    get_ratio_asset,
    get_density_dist,
    get_dividend_price,
    get_demolition_price
)


app = Flask(__name__)
url0 = os.getenv('PREVIEW_FRONTEND_URL', None)
url1 = os.getenv('FRONTEND_URL_1', None)
url2 = os.getenv('FRONTEND_URL_2', None)
url3 = os.getenv('FRONTEND_URL_3', None)
origins = ['http://localhost:3000']
if url0:
    origins.append(url0)
if url1:
    origins.append(url1)
if url2:
    origins.append(url2)
if url3:
    origins.append(url3)
CORS(
    app,
    origins=origins,
)


@app.route('/calculation', methods=['GET'])
def calculation():
    set_seed(1)

    stocks = [
        (
            urllib.parse.unquote(key),          # stock name (str)
            list(map(float, value.split(',')))  # stock data (list)
        )
        for key, value in request.args.to_dict().items()
    ]
    assets = [Asset(stock_name, *stock_data) for stock_name, stock_data in stocks]
    for A in assets:
        A.set_price_transition()

    res = {}

    # Using Transition Chart
    res['transition'] = get_total_transion(assets)

    # Using Pie Chart
    res['pie'] = get_ratio_asset(assets)

    # Using Density Chart
    res['density'] = get_density_dist(assets)

    # Using Bar Chart
    res['bar'] = get_dividend_price(assets)

    # Using Demolition Chart
    res['demolition'] = get_demolition_price(assets, duration=20)

    stock_json = jsonify(res)
    return stock_json, 200


@app.route('/re-calculation', methods=['GET'])
def re_calculation():

    params = [
        (
            urllib.parse.unquote(key),          # stock name (str)
            list(map(float, value.split(',')))  # stock data (list)
        )
        for key, value in request.args.to_dict().items()
    ]

    assets = [Asset(stock_name, *stock_data) for stock_name, stock_data in params[:-1]]
    for A in assets:
        A.set_price_transition()

    res = {}

    # Using Demolition Chart
    res['demolition'] = get_demolition_price(assets, duration=int(params[-1][1][0]))

    stock_json = jsonify(res)
    return stock_json, 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
