from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from models import db, User, Project, ProjectCompany
from werkzeug.security import generate_password_hash, check_password_hash
import json
from sqlalchemy import text

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
        name = request.form['name']
        role = request.form['role']  # donor, company, or charity
        password = request.form['password']

        # Only get wallet_address if the user is a charity or company
        wallet_address = None
        if role in ['charity', 'company']:
            wallet_address = request.form.get('wallet_address', '')

        # Check if email already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("Email already registered!")
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(password)
        user = User(
            email=email,
            name=name,
            role=role,
            password=hashed_password,
            wallet_address=wallet_address
        )
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

@app.route('/charity/<int:charity_id>')
def view_charity(charity_id):
    charity = User.query.filter_by(id=charity_id, role='charity').first_or_404()
    return render_template('charity_profile.html', charity=charity)

@app.route('/api/charity/<int:charity_id>/wallet')
def get_charity_wallet(charity_id):
    charity = User.query.filter_by(id=charity_id, role='charity').first_or_404()
    return jsonify({
        'name': charity.name,
        'wallet_address': charity.wallet_address
    })


# Update the dashboard route in app.py to redirect donors to the home page

@app.route('/dashboard')
@login_required
def dashboard():
    # Redirect donors to the home page
    if current_user.role == 'donor':
        return redirect(url_for('home'))

    # For charities, show their projects
    if current_user.role == 'charity':
        projects = Project.query.filter_by(user_id=current_user.id).all()
        return render_template('charity_dashboard.html', user=current_user, projects=projects)

    # For companies
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

    # Get all users with role='company'
    companies = User.query.filter_by(role='company').all()

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
            company_user_id = int(item['company_id'])
            percentage = float(item['percentage'])
            amount = (percentage / 100) * total_budget

            project_company = ProjectCompany(
                project_id=new_project.id,
                company_user_id=company_user_id,
                percentage=percentage,
                amount=amount
            )
            db.session.add(project_company)

        db.session.commit()
        flash("Project created successfully!")
        return redirect(url_for('dashboard'))

    return render_template('create_project.html', companies=companies)


@app.route('/home')
@login_required
def home():
    # Only donors can access this page
    if current_user.role != 'donor':
        flash("This page is only accessible to donors!")
        return redirect(url_for('dashboard'))

    # Get all projects
    projects = Project.query.all()

    return render_template('home.html', projects=projects)

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
    companies = User.query.filter_by(role='company').all()
    return jsonify([{'id': c.id, 'name': c.name} for c in companies])


# Add this route to your app.py file

@app.route('/project/<int:project_id>/donate', methods=['GET', 'POST'])
@login_required
def donate_project(project_id):
    # Only donors can access this page
    if current_user.role != 'donor':
        flash("Only donors can make donations!")
        return redirect(url_for('dashboard'))

    project = Project.query.get_or_404(project_id)
    charity = User.query.get(project.user_id)
    project_companies = ProjectCompany.query.filter_by(project_id=project_id).all()

    # Get company details for each project_company
    companies = []
    for pc in project_companies:
        company = User.query.get(pc.company_user_id)
        companies.append({
            'name': company.name,
            'wallet_address': company.wallet_address,
            'percentage': pc.percentage,
            'amount': pc.amount
        })

    if request.method == 'POST':
        donor_wallet = request.form['donor_wallet']
        amount = float(request.form['amount'])

        # In a real application, you would process the crypto transaction here
        # For now, we'll just show a success message

        flash(f"Thank you for your donation of ${amount} to {project.name}!")
        return redirect(url_for('home'))

    return render_template('donate.html',
                           project=project,
                           charity=charity,
                           companies=companies)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()

    app.run(debug=True)