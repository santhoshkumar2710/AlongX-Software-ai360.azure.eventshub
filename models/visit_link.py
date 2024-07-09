import sys
sys.path.append("..")
from database import BASE
from sqlalchemy import Column, BigInteger, String, Date,DateTime, ForeignKey, JSON,Integer
from sqlalchemy.orm import relationship
import datetime

class Visit_link(BASE):
    __tablename__ = "tbl_visits"
    visit_id = Column(Integer, primary_key=True, autoincrement=True)
    campaign_id = Column(Integer, ForeignKey('tbl_Campaign.campaign_id', ondelete='CASCADE'), nullable=False)
    visit_date = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    
    #campaign = relationship('Campaign', back_populates='Visit_link')