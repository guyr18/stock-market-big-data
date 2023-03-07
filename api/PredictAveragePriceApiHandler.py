from flask_restful import Api, Resource, reqparse
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Stock, Share
import pandas as pd
from sklearn.model_selection import train_test_split 
from sklearn.linear_model import LinearRegression
from DBConfig import DBConfig

class PredictAveragePriceApiHandler(Resource):

  def post(self):
    parser = reqparse.RequestParser()
    parser.add_argument('stock_name', type=str, location='json', required = True)
    parser.add_argument('predict_year', type=int, location='json', required = True)
    args = parser.parse_args()

    # Cache stock name to query database with, passed from client.
    stock_name = args['stock_name']
    predict_year = args['predict_year']

    # Establish SQLAlchemy connection.
    url = f"{DBConfig.CONNECTOR_SUBSTR}://{DBConfig.DB_USERNAME}:{DBConfig.DB_PWD}@{DBConfig.DB_HOST_IP}/{DBConfig.DB_NAME}"
    engine = create_engine(url)
    connection = engine.connect()

    # CREATE THE SESSION OBJECT
    Session = sessionmaker(bind=engine)
    session = Session()

    # Fetch stock id that is associated with stock_name.
    stockRecord = session.query(Stock.Stock).filter_by(stock_name = stock_name)

    # Fetch share history that is associated with previously fetched stock id.
    relatedShares = session.query(Share.Share).filter_by(stock_id = stockRecord[0].stock_id)

    lowsAndHighs = []

    for relation in relatedShares:
      lowsAndHighs.append([relation.Date.year, (relation.Low + relation.High) / 2])

    dataset = pd.DataFrame(lowsAndHighs, columns=['Year', 'Avg'])
    X = dataset['Year'].values.reshape(-1, 1)
    Y = dataset['Avg'].values.reshape(-1, 1)
    X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=0.2, random_state=0)
    regressor = LinearRegression()  
    regressor.fit(X_train, y_train)
    predicted_avg = regressor.intercept_ + regressor.coef_ * predict_year
    return {"predicted_avg": predicted_avg[0][0]}