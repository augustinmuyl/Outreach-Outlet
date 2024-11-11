from flask import Flask, render_template, redirect, request
from flask_sqlalchemy import SQLAlchemy
from flask_scss import Scss
import pandas as pd

# Initialize Flask app
app = Flask(__name__)
Scss(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)


class Organization(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)


# CSV -> DB
def csv_to_db(csv):
    try:
        data = pd.read_csv(csv)

        for _, r in data.iterrows():
            organization = Organization(
                name=r['Name'],
                category=r['Category'],
                address=r['Address'],
                phone_number=r['Phone Number']
            )
            db.session.add(organization)

        db.session.commit()
    except Exception as e:
        print(f"Error importing data: {e}")


with app.app_context():
    db.create_all()
    csv_to_db('Data.csv')


# Home page
@app.route('/', methods= ['GET', 'POST'])
def index():
    if request.method == 'POST':
        current_category = request.form.get('Category')
        return redirect( f'/results/{current_category}')
    else:
        return render_template('index.html')

    

# Results page
@app.route('/results/<category>', methods=['GET'])
def results(current_category):
    volunteering_list = Organization.query.filter_by(category=current_category).all()
    return render_template('results.html', volunteering_list=volunteering_list)
    
    

if __name__ == '__main__':
    app.run(debug=True, port=5001)  # Run the app in debug mode