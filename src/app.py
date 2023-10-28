"""
Flask App main modules
"""

import os
import urllib.parse

from flask import Flask, request, jsonify
from flask_cors import CORS

from utils import set_seed, make_logger
from asset_calc import (
    Asset,
    get_total_transion,
    get_ratio_asset,
    get_density_dist,
    get_dividend_price,
    get_demolition_price
)


app = Flask(__name__)
logger = make_logger()

# Create list of origins
env_vars = ['FRONTEND_URL_1', 'FRONTEND_URL_2',
            'FRONTEND_URL_3', 'LOCAL_HOST', 'POSTMAN_HEADER']
origins = [os.getenv(var) for var in env_vars if os.getenv(var) is not None]

# get firebase info
firebase_project_name = os.getenv('FIREBASE_PROJECT_NAME', None)


@app.after_request
def add_cors_headers(response):
    referrer = request.referrer.rstrip('/')
    if origin_is_allowed(referrer):
        response.headers.add('Access-Control-Allow-Origin', referrer)
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET,PUT,POST,DELETE,OPTIONS')
    return response


def origin_is_allowed(origin: str) -> bool:
    parsed_uri = urllib.parse.urlparse(origin)
    domain = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
    # check if firebase project name is in origin
    if firebase_project_name and domain.startswith(f'https://{firebase_project_name}--'):
        return True
    else:
        return domain in origins


CORS(app, origins=origins)


def get_params() -> list[tuple[str, list[float]]]:
    """ Parse request parameters
    """
    params = [
        (
            urllib.parse.unquote(key),          # stock name (str)
            list(map(float, value.split(',')))  # stock data (list)
        )
        for key, value in request.args.to_dict().items()
    ]
    return params


@app.route('/calculation', methods=['GET'])
def calculation():
    """ Return response of calculation
    """
    set_seed(1)
    try:
        params = get_params()
        logger.info(f'calculation params: {params}')

        assets = [Asset(stock_name, *stock_data)
                  for stock_name, stock_data in params]
        for A in assets:
            A.set_price_transition()

        res = {}
        res['transition'] = get_total_transion(
            assets)  # Using Transition Chart
        res['pie'] = get_ratio_asset(assets)            # Using Pie Chart
        res['density'] = get_density_dist(assets)       # Using Density Chart
        res['bar'] = get_dividend_price(assets)         # Using Bar Chart
        res['demolition'] = get_demolition_price(
            assets, duration=20)                        # Using Demolition Chart

        stock_json = jsonify(res)
        logger.info('calculation success')

        return stock_json, 200

    except Exception as e:
        logger.error(f'calculation error: {e}', exc_info=True)
        return jsonify({'error': str(e)}), 500


@app.route('/re-calculation', methods=['GET'])
def re_calculation():
    """ Return response of re-calculation
    """
    try:
        params = get_params()
        logger.info(f'calculation params: {params}')

        assets = [Asset(stock_name, *stock_data)
                  for stock_name, stock_data in params[:-1]]
        for A in assets:
            A.set_price_transition()

        res = {}
        res['demolition'] = get_demolition_price(
            assets, duration=int(params[-1][1][0]))     # Using Demolition Chart

        stock_json = jsonify(res)
        return stock_json, 200

    except Exception as e:
        logger.error(f'calculation error: {e}', exc_info=True)
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
