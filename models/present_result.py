import sys
sys.path.append("..")
from database import BASE
from sqlalchemy import Column, BigInteger, String, Date, ForeignKey, JSON,Integer
from sqlalchemy.orm import relationship

class PresentResult(BASE):
    __tablename__="tbl_present_result"
    Present_Result_id=Column(Integer,primary_key=True, autoincrement=True)
    campaign_id= Column(Integer, ForeignKey('tbl_Campaign.campaign_id',ondelete="CASCADE"),nullable=False)
    question_id=Column(Integer,ForeignKey('tbl_builder.question_id',ondelete="SET NULL"),nullable=False)
    analyse_id=Column(Integer,ForeignKey('tbl_analysis.analysis_id',ondelete="SET NULL"))
    chart_type = Column(String(300),default="pie")
    present_result=Column(JSON)

    campaign = relationship("Campaign", back_populates="present_results")
    