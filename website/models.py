from . import db
from flask_login import UserMixin
import datetime as dt


#------------------------ Database Tables -----------------------------------------------
class User(db.Model, UserMixin):
    __tablename__='user'
    usr_id=db.Column(db.Integer, nullable=False,primary_key=True, autoincrement=True)
    usr_name=db.Column(db.String, nullable=False, unique=True)
    name=db.Column(db.String, nullable=False)
    mail=db.Column(db.String, nullable=False, unique=True)
    password=db.Column(db.String, nullable=False)
    role=db.Column(db.String, nullable=False)

    # Define relationship to Campaign
    campaigns = db.relationship('Campaign', back_populates='user', lazy=True)

    # Define relationship to Influencer
    influencer = db.relationship('Influencer', back_populates='user', uselist=False)

    # Define relationship with Ad Request
    ad_requests = db.relationship('Ad_request', back_populates='sponsor')

    def get_id(self):
        return str(self.usr_id)


class Influencer(db.Model):
    __tablename__='influencer'
    influencer_id=db.Column(db.Integer, nullable=False, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.usr_id'), nullable=False)
    name=db.Column(db.String,nullable=False)
    mail_id=db.Column(db.String,nullable=False)
    category=db.Column(db.String,nullable=True)
    niche=db.Column(db.String, nullable=True)
    reach=db.Column(db.Integer, nullable=True)    
    is_flag=db.Column(db.Boolean,default=False)
    # Define the relationship to User
    user = db.relationship('User', back_populates='influencer', uselist=False)

    # Define relationship with Ad-Request
    ad_requests = db.relationship('Ad_request', back_populates='influencer')


class Campaign(db.Model): 
    __tablename__='campaign'
    campaign_id=db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    campaign_name=db.Column(db.String, nullable=False)
    description=db.Column(db.String, nullable=False)
    start_date=db.Column(db.Date, nullable=False)
    end_date=db.Column(db.Date, nullable=False)
    budget=db.Column(db.Integer, nullable=False)
    visibility=db.Column(db.String, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.usr_id'), nullable=False)
    
    # Define relationship to User
    user = db.relationship('User', back_populates='campaigns')


    def __init__(self, campaign_name: str, description: str, start_date: dt.date, 
                 end_date: dt.date, budget: int, visibility: str,
                 user_id:int):
        self.campaign_name = campaign_name
        self.description = description
        self.start_date = start_date
        self.end_date = end_date
        self.budget = budget
        self.visibility = visibility
        self.user_id=user_id


class Ad_request(db.Model):
    __tablename__='ad_request'
    ad_id=db.Column(db.Integer,primary_key=True, autoincrement=True)
    sponsor_id = db.Column(db.Integer, db.ForeignKey('user.usr_id'), nullable=False)
    campaign_id=db.Column(db.Integer,db.ForeignKey('campaign.campaign_id'),nullable=False)
    influencer_id=db.Column(db.Integer,db.ForeignKey('influencer.influencer_id'),nullable=False)
    message=db.Column(db.String, nullable=False)
    requirements=db.Column(db.String, nullable=False)
    amount=db.Column(db.String, nullable=False)
    status=db.Column(db.String, nullable=False)

    # Define relationship with Sponsor
    sponsor = db.relationship('User', back_populates='ad_requests')

    # Define relationship with Influencer
    influencer = db.relationship('Influencer', back_populates='ad_requests')

    # Define relationship with Campaign
    campaign = db.relationship('Campaign', backref='ad_requests')


# db.create_all()