import azure.functions as func
import logging
import json
import requests
from fastapi.templating import Jinja2Templates
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey
from models.campaign import Campaign
from models.audience_segmentation import Audience_segmentation
from models.audience import Audience
import urllib.parse

app = func.FunctionApp()

# Database connection details for SQL Server
host = "ai360-prod-ci-sqlserver.database.windows.net"
username = "ai360-admin"
password = "Alongx2024"
port = 1433
database = "ai360-prod-ci-sqldatabase"
encoded_username = urllib.parse.quote_plus(username)
encoded_password = urllib.parse.quote_plus(password)

SQLALCHEMY_DATABASE_URL = f"mssql+pyodbc://{encoded_username}:{encoded_password}@{host}:1433/{database}?driver=ODBC Driver 18 for SQL Server"

# SQLAlchemy setup
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"ssl_ca": "DigiCertGlobalRootCA.crt.pem"})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

# Logic App endpoint
LA_ENDPOINT = "https://prod-14.centralindia.logic.azure.com:443/workflows/50bf8bdef5454c1088fb42122f79deef/triggers/When_a_HTTP_request_is_received/paths/invoke?api-version=2016-10-01&sp=%2Ftriggers%2FWhen_a_HTTP_request_is_received%2Frun&sv=1.0&sig=GpMchJkW9zc57kYyWG5zzs3BKzQiYH86J-SXWjOf5l4"

templates = Jinja2Templates(directory="template")

class SendNotification:
    def __init__(self):
        self.lg_endpoint = LA_ENDPOINT

    def global_requests(self, payload):
        try:
            response = requests.post(self.lg_endpoint, json=payload)
            response.raise_for_status()
            return {"message": "Notification sent successfully", "response": response}
        except requests.exceptions.RequestException as e:
            return {"message": "Failed to send notification", "error": str(e)}

    def send_email_to_audience(self, to_email=None, audience_name=None, campaign_name=None, survey_link=None):
        try:
            logging.info('Sending email to audience...')
            logging.info(f'To Email: {to_email}, Audience Name: {audience_name}, Campaign Name: {campaign_name}, Survey Link: {survey_link}')

            subject_msg = "Join Us in Shaping the Future of AI360: Participate in Our Campaigns Today!"

            logging.info('Loading template...')
            try:
                html_content = templates.get_template("audience_email.html").render(
                    {"request": None, "audience_name": audience_name, "campaign_name": campaign_name, "survey_link": survey_link}
                )
                logging.info('Template loaded and rendered.')
            except Exception as template_error:
                logging.error(f"Error loading or rendering template: {template_error}")
                raise template_error

            # Ensure that all values are strings
            to_email_str = str(to_email) if to_email else ""
            audience_name_str = str(audience_name) if audience_name else ""
            campaign_name_str = str(campaign_name) if campaign_name else ""
            survey_link_str = str(survey_link) if survey_link else ""

            payload = {
                "to_mail": to_email_str,
                "subject": subject_msg,
                "body": html_content,
            }

            logging.info(f"Payload for email: {payload}")
            return self.global_requests(payload)

        except Exception as e:
            logging.error(f"Error sending email: {str(e)}")
            return {"message": "Failed to send email", "error": str(e)}

@app.event_hub_message_trigger(arg_name="azeventhub", event_hub_name="send_multiple_emails",
                               connection="ai360prodciehn_RootManageSharedAccessKey_EVENTHUB") 
def eventhub_trigger(azeventhub: func.EventHubEvent):
    logging.info('Python EventHub trigger processed an event: %s', azeventhub.get_body().decode('utf-8'))
    
    # Parse message
    logging.info('Parsing message...')
    messages = azeventhub.get_body().decode('utf-8')
    logging.info('Parsed JSON data: %s', messages)
    data = json.loads(messages)
    logging.info('Data after JSON load: %s', data)
    campaign_id = data.get('campaign_id')
    logging.info('Campaign ID extracted: %s', campaign_id)

    # Database session
    logging.info('Creating database session...')
    db = SessionLocal()
    logging.info('Database session created.')

    try:
        # Retrieve campaign and audience details from the database
        logging.info('Querying database for campaign...')
        campaign = db.query(Campaign).filter(Campaign.campaign_id == campaign_id).first()
        logging.info('Querying database for campaign...1')

        if not campaign:
            logging.error("Campaign not found")
            return
        logging.info('Querying database for campaign...2')
        
        audience_ids = set()
        logging.info('Campaign segment IDs: %s', campaign.segment_id)
        
        for segment_dict in campaign.segment_id:
            logging.info('Processing segment dictionary: %s', segment_dict)
            
            # Extract the segment_id value from the dictionary
            segment_id_value = segment_dict.get('segment_id')
            logging.info('Extracted segment_id_value: %s', segment_id_value)

            if segment_id_value is not None:
                logging.info(f'Querying database for segment...{segment_id_value}')
                segment = db.query(Audience_segmentation).filter(Audience_segmentation.segment_id == segment_id_value).first()
                logging.info('Querying database for segment...3')  
                if segment:
                    for audience_data in segment.audience_id:
                        audience_ids.add(audience_data["audience_id"])

        if not audience_ids:
            logging.info('No audience IDs found for the campaign segments.')
            return
        
        logging.info('Collected audience IDs: %s', audience_ids)
        
        email_ids = set()
        for audience_id in audience_ids:
            audience = db.query(Audience).filter(Audience.audience_id == audience_id).first()
            logging.info('Querying database for audience...4')
            if audience:
                email_ids.add(audience.email)

        if not email_ids:
            logging.info('No email IDs found for the audience IDs.')
            return
        
        logging.info('Collected email IDs: %s', email_ids)
        
        email_sender = SendNotification()
        
        for email_id in email_ids:
            audience = db.query(Audience).filter(Audience.email == email_id).first()
            logging.info('Querying database for audience...5')
                
            if audience:
                logging.info(f'Sending email to: {email_id}')
                result = email_sender.send_email_to_audience(to_email=audience.email, audience_name=audience.audience_name, campaign_name=campaign.campaign_name, survey_link=campaign.survey_link)
                logging.info(f'Email send result: {result}')

    except Exception as e:
        logging.error(f"Error processing event: {str(e)}")
    finally:
        logging.info('Closing database session...')
        db.close()