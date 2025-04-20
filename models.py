from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(100))
    role = db.Column(db.String(20))  # donor, company, or charity
    wallet_address = db.Column(db.String(100))

    # Add relationships
    projects = db.relationship('Project', backref='charity', lazy=True)
    donations = db.relationship('Donation', backref='donor', lazy=True)


class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    description = db.Column(db.Text)
    total_budget = db.Column(db.Float)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    contract_address = db.Column(db.String(100))

    # Add relationships
    project_companies = db.relationship('ProjectCompany', backref='project', lazy=True)
    donations = db.relationship('Donation', backref='project', lazy=True)


class ProjectCompany(db.Model):
    __tablename__ = 'project_company'

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    company_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    percentage = db.Column(db.Float, nullable=False)
    amount = db.Column(db.Float, nullable=False)

    # Add relationship to User model for the company
    company_user = db.relationship('User', foreign_keys=[company_user_id])


class Donation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    # Foreign keys
    donor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)