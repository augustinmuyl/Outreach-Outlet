from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


# Association table
opportunity_categories = db.Table('opportunity_categories', 
    db.Column('opportunity_id', db.Integer, db.ForeignKey('opportunity.id'), primary_key=True),
    db.Column('category_id', db.Integer, db.ForeignKey('category.id'), primary_key=True))


class Opportunity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(), nullable=False)
    organization = db.Column(db.String(), nullable=False)
    description = db.Column(db.Text)
    categories = db.relationship('Category', secondary=opportunity_categories, back_populates='opportunities')

    def __repr__(self):
        return f"{self.title} ({self.organization})"


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    opportunities = db.relationship('Opportunity', secondary=opportunity_categories, back_populates='categories')

    def __repr__(self):
        return f"{self.name}"

