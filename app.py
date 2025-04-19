from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from models import db, User, Company, Project, ProjectCompany
from werkzeug.security import generate_password_hash, check_password_hash
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'this-should-be-secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# ----------------------
# Routes Below
# ----------------------

@app.route('/')
def index():
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        role = request.form['role']  # donor, company, or charity
        password = request.form['password']
        hashed_password = generate_password_hash(password)
        user = User(email=email, role=role, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash("Registered successfully!")
        return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if not user or not check_password_hash(user.password, password):
            flash("Invalid credentials!")
            return redirect(url_for('login'))
        login_user(user)
        return redirect(url_for('dashboard'))
    return render_template('login.html')


@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == 'charity':
        projects = Project.query.filter_by(user_id=current_user.id).all()
        return render_template('charity_dashboard.html', user=current_user, projects=projects)
    return render_template('dashboard.html', user=current_user)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/projects/new', methods=['GET', 'POST'])
@login_required
def create_project():
    if current_user.role != 'charity':
        flash("Only charities can create projects!")
        return redirect(url_for('dashboard'))

    companies = Company.query.all()

    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        total_budget = float(request.form['total_budget'])

        # Create project
        new_project = Project(
            name=name,
            description=description,
            total_budget=total_budget,
            user_id=current_user.id
        )
        db.session.add(new_project)
        db.session.flush()  # This gives us the new project's ID

        # Get company selections and percentages
        company_data = json.loads(request.form['company_data'])

        # Create project-company relationships
        for item in company_data:
            company_id = int(item['company_id'])
            percentage = float(item['percentage'])
            amount = (percentage / 100) * total_budget

            project_company = ProjectCompany(
                project_id=new_project.id,
                company_id=company_id,
                percentage=percentage,
                amount=amount
            )
            db.session.add(project_company)

        db.session.commit()
        flash("Project created successfully!")
        return redirect(url_for('dashboard'))

    return render_template('create_project.html', companies=companies)


@app.route('/projects/<int:project_id>')
@login_required
def view_project(project_id):
    project = Project.query.get_or_404(project_id)
    if project.user_id != current_user.id and current_user.role != 'admin':
        flash("You don't have permission to view this project!")
        return redirect(url_for('dashboard'))

    project_companies = ProjectCompany.query.filter_by(project_id=project_id).all()
    return render_template('view_project.html', project=project, project_companies=project_companies)


@app.route('/api/companies')
@login_required
def get_companies():
    companies = Company.query.all()
    return jsonify([{'id': c.id, 'name': c.name} for c in companies])


if __name__ == '__main__':
    with app.app_context():
        db.create_all()

        # Add some sample companies if they don't exist
        if not Company.query.first():
            sample_companies = [
                Company(name="Education First", description="Education focused charity"),
                Company(name="Health Matters", description="Health focused charity"),
                Company(name="Environmental Trust", description="Environmental focused charity"),
                Company(name="Animal Welfare Group", description="Animal welfare focused charity")
            ]
            db.session.add_all(sample_companies)
            db.session.commit()

    app.run(debug=True)