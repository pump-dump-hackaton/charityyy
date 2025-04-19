from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

# Create the SQLAlchemy instance
db = SQLAlchemy()


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    name = db.Column(db.String(100))
    password = db.Column(db.String(100))
    role = db.Column(db.String(50))  # donor, company, or charity
    wallet_address = db.Column(db.String(255))  # Added wallet_address field

    # Define relationship to projects (for charities)
    projects = db.relationship('Project', backref='owner', lazy=True)


class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    description = db.Column(db.Text)
    total_budget = db.Column(db.Float)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # Define relationship to project_companies
    companies = db.relationship('ProjectCompany', backref='project', lazy=True)


class ProjectCompany(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    company_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    percentage = db.Column(db.Float)
    amount = db.Column(db.Float)

    # Define relationship to company (User with role='company')
    company = db.relationship('User', backref='project_companies')