from flask_restful import Api, Resource, reqparse
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Stock, Share
from .DBConfig import DBConfig

class GetStockShareApiHandler(Resource):

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
    stockRecord = session.query(Stock.Stock).filter_by(stock_name = stock_name)

    # Fetch share history that is associated with previously fetched stock id.
    relatedShares = session.query(Share.Share).filter_by(stock_id = stockRecord[0].stock_id)

    print(f"number of related shares: {relatedShares.count()}")
    minYear, maxYear = None, None
    numRelatedShares = relatedShares.count()
    yearPercents = {}
    yearVolumes = {}
    yearAvgs = {}
    monthVolumes = {}
    stockAttributeAvgs = {'Low': 0, 'High': 0, 'Open': 0, 'Close': 0}
    relationsForCurrentYear = [0, None]

    for relation in relatedShares:
      
      date = relation.Date # Track current date for this relation / row.
      minYear = date.year if minYear == None else minYear # Update minimum year processed.
      maxYear = date.year if maxYear == None else max(date.year, maxYear) # Update maximum year processed.
      stockAttributeAvgs['Low'] += relation.Low
      stockAttributeAvgs['High'] += relation.High
      stockAttributeAvgs['Open'] += relation.Open
      stockAttributeAvgs['Close'] += relation.Close

      # Is this a new year that we have reached?
      if date.year != relationsForCurrentYear[1]:

        if relationsForCurrentYear[1] != None:
          yearAvgs[relationsForCurrentYear[1]] /= numRelatedShares

        # Update current year and number of relations processed for this year.
        relationsForCurrentYear = [1, date.year]

      else:
        relationsForCurrentYear[0] += 1

      if date.year not in yearPercents:
        yearPercents[date.year] = 1 / numRelatedShares
      else:
        yearPercents[date.year] += 1 / numRelatedShares

      if date.year not in yearVolumes:
        yearVolumes[date.year] = relation.Volume
      else:
        yearVolumes[date.year] += relation.Volume

      if date.month not in monthVolumes:
        monthVolumes[date.month] = relation.Volume
      else:
        monthVolumes[date.month] += relation.Volume

      if date.year not in yearAvgs:
        yearAvgs[date.year] = (relation.Low + relation.High) / 2
      else:
        yearAvgs[date.year] += (relation.Low + relation.High) / 2

    yearAvgs[relationsForCurrentYear[1]] /= numRelatedShares
    stockAttributeAvgs['Low'] /= numRelatedShares
    stockAttributeAvgs['High'] /= numRelatedShares
    stockAttributeAvgs['Open'] /= numRelatedShares
    stockAttributeAvgs['Close'] /= numRelatedShares
    response = {"status": "Success", "stockAttributeAvgs": stockAttributeAvgs, "yearAvgs": yearAvgs, "yearPercents": yearPercents, "yearVolumes": yearVolumes, "monthVolumes": monthVolumes, "minYear": minYear, "maxYear": maxYear, "numRelatedShares": numRelatedShares}

    # Return response to client.
    return response
