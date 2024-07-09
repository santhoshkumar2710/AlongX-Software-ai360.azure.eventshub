import sys
sys.path.append("..")
from database import BASE
from sqlalchemy import Column, BigInteger, String, Date, ForeignKey, JSON,Integer
from sqlalchemy.orm import relationship
from models.present_result import PresentResult
from models.visit_link import Visit_link

class Campaign(BASE):
    __tablename__ = "tbl_Campaign"
    campaign_id = Column(Integer, primary_key=True, autoincrement=True)
    account_id = Column(Integer, ForeignKey('tbl_Registration.account_id'),nullable=False)
    user_id = Column(Integer, nullable=False)
    campaign_name = Column(String(255), nullable=False)
    campaign_nature = Column(String(255),nullable=False)
    category = Column(String(255), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    created_date = Column(Date,nullable=False)
    modified_date = Column(Date,nullable=False)
    description = Column(String(1000), nullable=True)
    survey_link = Column(String(50),nullable=True)
    feedback_link = Column(String(50), nullable=True)
    segment_id = Column(JSON,nullable=True)
    visit_count = Column(Integer, default=0, nullable=True)
    present_results = relationship("PresentResult", cascade="all, delete-orphan")
    #visits = relationship("Visit_link", cascade="all, delete-orphan") 

    # present_results = relationship("PresentResult", back_populates="campaign", cascade="all, delete-orphan")
    # Visit_link = relationship('Visit_link', back_populates='campaign', cascade="all, delete-orphan")