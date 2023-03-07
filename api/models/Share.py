from sqlalchemy.ext.declarative import declarative_base
import sqlalchemy as db

Base = declarative_base()

class Share(Base):

    __tablename__ = "shares"
    share_id = db.Column(db.Integer, primary_key=True)
    stock_id = db.Column(db.Integer)
    Date = db.Column(db.Date)
    Low = db.Column(db.Float)
    High = db.Column(db.Float)
    Open = db.Column(db.Float)
    Close = db.Column(db.Float)
    Volume = db.Column(db.Integer)
