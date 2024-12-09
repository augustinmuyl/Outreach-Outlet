from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin


db = SQLAlchemy()


# Association tables
opportunity_categories = db.Table('opportunity_categories', 
    db.Column('opportunity_id', db.Integer, db.ForeignKey('opportunity.id'), primary_key=True),
    db.Column('category_id', db.Integer, db.ForeignKey('category.id'), primary_key=True))


user_opportunities = db.Table('user_opportunities',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('opportunity_id', db.Integer, db.ForeignKey('opportunity.id'), primary_key=True))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    email = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(150), nullable=False)
    saved_opportunities = db.relationship('Opportunity', secondary=user_opportunities, back_populates='users')


class Opportunity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(), nullable=False)
    organization = db.Column(db.String(), nullable=False)
    org_logo = db.Column(db.String())
    description = db.Column(db.Text)
    categories = db.relationship('Category', secondary=opportunity_categories, back_populates='opportunities')
    users = db.relationship('User', secondary=user_opportunities, back_populates='saved_opportunities')


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    opportunities = db.relationship('Opportunity', secondary=opportunity_categories, back_populates='categories')

    def __repr__(self):
        return f"{self.name}"

