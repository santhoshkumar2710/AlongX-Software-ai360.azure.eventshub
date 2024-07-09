import sys
sys.path.append("..")
from database import BASE
from sqlalchemy import Column, BigInteger, String, Date, ForeignKey, JSON,Integer
from sqlalchemy.orm import relationship

class Audience_segmentation(BASE):
    __tablename__="tbl_audienceSegmentation"
    segment_id=Column(Integer, primary_key=True, autoincrement=True)
    account_id = Column(Integer, ForeignKey('tbl_Registration.account_id'),nullable=False)
    segment_name=Column(String(500))
    audience_id = Column(JSON)