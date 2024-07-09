import sys
sys.path.append("..")
from database import BASE
from sqlalchemy import Column, BigInteger, String, Date, ForeignKey,UniqueConstraint,func,Integer,DateTime
from sqlalchemy.orm import relationship

class Audience(BASE):
    __tablename__="tbl_audience"
    audience_id=Column(Integer, primary_key=True, autoincrement=True)
    account_id = Column(Integer, ForeignKey('tbl_Registration.account_id'),nullable=False)
    audience_name=Column(String(500))
    email = Column(String(500), nullable=True)
    phone_number = Column(String(10),nullable=True)
    gender = Column(String(50))
    date_of_birth=Column(Date)
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    country = Column(String(100), nullable=True)
    upload_date = Column(DateTime, default=func.now())

   
    __table_args__ = (
        UniqueConstraint('account_id', 'phone_number', name='uix_account_phone'),
    )

