from flask_restful import Api, Resource, reqparse
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Stock
from .DBConfig import DBConfig

class ValidateSearchInputApiHandler(Resource):

  def post(self):
    parser = reqparse.RequestParser()
    parser.add_argument('stock_name', type=str, location='json', required = True)
    args = parser.parse_args()

    # Cache stock name to query database with, passed from client.
    stock_name = args['stock_name']

    # Establish SQLAlchemy connection.
    url = f"{DBConfig.CONNECTOR_SUBSTR}://{DBConfig.DB_USERNAME}:{DBConfig.DB_PWD}@{DBConfig.DB_HOST_IP}/{DBConfig.DB_NAME}"
    engine = create_engine(url)
    connection = engine.connect()

    # CREATE THE SESSION OBJECT
    Session = sessionmaker(bind=engine)
    session = Session()

    # Fetch stock id that is associated with stock_name.
    stockRecord = session.query(Stock.Stock).filter_by(stock_name = str(stock_name).lower())

    return {"isValid": stockRecord.count() == 1}