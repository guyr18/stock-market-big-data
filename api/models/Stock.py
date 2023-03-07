from sqlalchemy.ext.declarative import declarative_base
import sqlalchemy as db

Base = declarative_base()

class Stock(Base):

    __tablename__ = "stocks"
    stock_id = db.Column(db.Integer, primary_key=True)
    stock_name = db.Column(db.String)
