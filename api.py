from database import db, Opportunity, Category
import requests


class Volunteer_API:
    def __init__(self, base_url):
        self.base_url = base_url
    
    def fetch_data(self):
        page = 1
        results = []

        while True:
            response = requests.get(f'{self.base_url}?page={page}')
            response.raise_for_status()
            data = response.json()

            for result in data['results']:
                results.append(result)
            
            page += 1
            
            if not data['next']:
                break
        
        return results


class Data_Processor:
    def __init__(self, volunteer_api):
        self.volunteer_api = volunteer_api
    
    def process_data(self):
        data = self.volunteer_api.fetch_data() # API results

        fetched_opportunities = {result['title'] for result in data}

        # Delete opportunities that are no longer in the API results
        for opportunity in Opportunity.query.all():
            if opportunity.title not in fetched_opportunities:
                db.session.delete(opportunity)

        # Add or update opportunities
        with db.session.no_autoflush:
            for result in data:

                opportunity = Opportunity.query.filter_by(title=result['title']).first()
                if not opportunity:
                    opportunity = Opportunity(
                        title=result['title'],
                        organization=result['organization']['name'],
                        description=result['description'],
                    )
                    db.session.add(opportunity)
                else:
                    opportunity.title = result['title']
                    opportunity.organization = result['organization']['name']
                    opportunity.description = result['description']

                for activity in result['activities']:

                    category = Category.query.filter_by(name=activity['category']).first()
                    if not category:
                        category = Category(name=activity['category'])
                        db.session.add(category)

                    if category not in opportunity.categories:
                        opportunity.categories.append(category)
            
        db.session.commit()
    
    def get_opportunities_from_category(self, category_name):

        category = Category.query.filter_by(name=category_name).first()

        if category:
            return category.opportunities
        else:
            return None
    
    def get_categories(self):

        categories = db.session.query(Category.name).distinct().all()

        return [category.name for category in categories]



