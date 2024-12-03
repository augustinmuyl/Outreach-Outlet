from flask import Flask, render_template, redirect, request
from flask_scss import Scss
from database import db, Opportunity, Category
from api import Volunteer_API, Data_Processor


# Initialize Flask app
def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
    Scss(app)

    db.init_app(app)

    with app.app_context():
        db.create_all()
    
    return app


app = create_app()
with app.app_context():
    base_url = 'https://www.volunteerconnector.org/api/search/'
    api = Volunteer_API(base_url)
    data_processor = Data_Processor(api)
    #data_processor.process_data()


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


if __name__ == '__main__':
    app.run(debug=True, port=5001)  # Run the app in debug mode