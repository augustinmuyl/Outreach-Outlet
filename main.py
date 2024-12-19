from flask import Flask, render_template, redirect, request, flash
from flask_scss import Scss
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, Email, EqualTo
from database import db, Opportunity, Category, User
from api import Volunteer_API, Data_Processor


# Initialize Flask app
def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
    app.config['SECRET_KEY'] = 'secret_key'
    Scss(app)

    db.init_app(app)

    with app.app_context():
        db.create_all()
    
    return app


app = create_app()
login_manager = LoginManager(app)
login_manager.login_view = 'login'
with app.app_context():
    base_url = 'https://www.volunteerconnector.org/api/search/'
    api = Volunteer_API(base_url)
    data_processor = Data_Processor(api)
    #data_processor.process_data()


# User loader and Forms
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=150)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6, max=150)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign up')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


# Home page
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        current_category = request.form.get('current_category')
        return redirect(f'/results/{current_category}')
    else:
        return render_template('index.html', categories=data_processor.get_categories())


# Results page
@app.route('/results/<current_category>', methods=['GET', 'POST'])
def results(current_category):
    if request.method == 'POST':
        new_category = request.form.get('new_category', current_category)
        return redirect(f'/results/{new_category}')
    else:
        volunteering_list = data_processor.get_opportunities_from_category(current_category)
        return render_template('results.html', volunteering_list=volunteering_list,
                            current_category=current_category, num_opportunities=len(volunteering_list),
                            categories=data_processor.get_categories())


# Opportunity page
@app.route('/opportunity/<opportunity_id>', methods=['GET', 'POST'])
def opportunity(opportunity_id):
    return render_template('opportunity.html', opportunity=data_processor.get_opportunity(opportunity_id))


# Registration page
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        existing_user = User.query.filter(
            (User.username == form.username.data) | (User.email == form.email.data)
            ).first()
        if existing_user:
            if existing_user.username == form.username.data:
                flash('Username already taken. Please choose another.', 'danger')
            if existing_user.email == form.email.data:
                flash('Email already registered. Please use another.', 'danger')
        else:
            hashed_password = generate_password_hash(form.password.data, method='pbkdf2:sha256')
            new_user = User(username=form.username.data, email=form.email.data, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()
            flash('Account created successfully!', 'success')
            return redirect('/')
    return render_template('register.html', form=form)


# Login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            flash('Login Successful!', 'success')
            return redirect('/')
        else:
            flash('Login Unsuccessful. Check email and password', 'danger')
    return render_template('login.html', form=form)


# Pofile page
@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    return render_template('profile.html', user=current_user)


# Logout page
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect('/')


# Delete account page
@app.route('/delete_account', methods=['GET', 'POST'])
@login_required
def delete_account():
    db.session.delete(current_user)
    db.session.commit()
    flash('Account deleted successfully.', 'info')
    return redirect('/')


# User opportunities page
@app.route('/saved_opportunities', methods=['GET', 'POST'])
@login_required
def my_opportunities():
    user_opportunities = current_user.saved_opportunities
    return render_template('saved_opportunities.html', opportunities=user_opportunities)


# Add opportunity page
@app.route('/save_opportunity/<opportunity_id>', methods=['GET', 'POST'])
@login_required
def add_opportunity(opportunity_id):
    user_opportunities = current_user.saved_opportunities
    opportunity = Opportunity.query.get_or_404(opportunity_id)
    if opportunity not in user_opportunities:
        user_opportunities.append(opportunity)
        db.session.commit()
        flash('Opportunity saved successfully!', 'success')
    else:
        flash('Opportunity already saved.', 'info')
    return redirect(f'/opportunity/{opportunity_id}')


# Remove opportunity page
@app.route('/remove_opportunity/<opportunity_id>', methods=['GET', 'POST'])
@login_required
def remove_opportunity(opportunity_id):
    user_opportunities = current_user.saved_opportunities
    opportunity = Opportunity.query.get_or_404(opportunity_id)
    if opportunity in user_opportunities:
        user_opportunities.remove(opportunity)
        db.session.commit()
        flash('Opportunity removed successfully!', 'success')
    else:
        flash('Opportunity not saved.', 'info')
    return redirect('/saved_opportunities')


# User opportunity page
@app.route('/user_opportunity/<opportunity_id>', methods=['GET', 'POST'])
@login_required
def user_opportunity(opportunity_id):
    opportunity = Opportunity.query.get_or_404(opportunity_id)
    return render_template('user_opportunity.html', opportunity=opportunity)


if __name__ == '__main__':
    app.run(debug=True, port=5001)  # Run the app in debug mode