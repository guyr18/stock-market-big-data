from flask import Flask, send_from_directory
from flask_restful import Api, Resource, reqparse
from flask_cors import CORS #comment this on deployment
from api.GetStockShareApiHandler import GetStockShareApiHandler
from api.ValidateSearchInputApiHandler import ValidateSearchInputApiHandler
from api.PredictAveragePriceApiHandler import PredictAveragePriceApiHandler

app = Flask(__name__, static_url_path='', static_folder='smd-react/public')
CORS(app) #comment this on deployment
api = Api(app)

@app.route("/", defaults={'path':''})
def serve(path):
    return send_from_directory(app.static_folder,'index.html')

api.add_resource(GetStockShareApiHandler, '/api/get_stock_shares')
api.add_resource(ValidateSearchInputApiHandler, '/api/validate_src_input')
api.add_resource(PredictAveragePriceApiHandler, '/api/predict_avg_price')