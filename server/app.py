import os
from dotenv import load_dotenv
from flask import Flask, jsonify, request, make_response, render_template
from flask_migrate import Migrate
from flask_restful import Api, Resource
from flask_cors import CORS  # Import CORS extension
from models import db, Bird

app = Flask(
    __name__,
    static_url_path='',
    static_folder='../client/build',
    template_folder='../client/build'
)


@app.route('/')
@app.route('/<int:id>')
def index(id=0):
    return render_template("index.html")
    
# Load environment variables
load_dotenv()

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URI')

# Check if the database URI is set
if app.config['SQLALCHEMY_DATABASE_URI'] is None:
    raise ValueError("DATABASE_URI environment variable not set!")

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

# Initialize CORS extension
CORS(app)

# Initialize Flask-Migrate
migrate = Migrate(app, db)

# Initialize Flask-SQLAlchemy
db.init_app(app)

# Error handler for 404
@app.errorhandler(404)
def not_found(e):
    return render_template("index.html")

# Initialize Flask-RESTful
api = Api(app)

class Birds(Resource):
    def get(self):
        try:
            birds = [bird.to_dict() for bird in Bird.query.all()]
            return make_response(jsonify(birds), 200)
        except Exception as e:
            return make_response(jsonify({'error': str(e)}), 500)

    def post(self):
        try:
            data = request.get_json()
            new_bird = Bird(
                name=data['name'],
                species=data['species'],
                image=data['image'],
            )
            db.session.add(new_bird)
            db.session.commit()
            return make_response(new_bird.to_dict(), 201)
        except Exception as e:
            db.session.rollback()
            return make_response(jsonify({'error': str(e)}), 500)

api.add_resource(Birds, '/birds')

class BirdByID(Resource):
    def get(self, id):
        try:
            bird = Bird.query.filter_by(id=id).first().to_dict()
            return make_response(jsonify(bird), 200)
        except Exception as e:
            return make_response(jsonify({'error': str(e)}), 500)

    def patch(self, id):
        try:
            data = request.get_json()
            bird = Bird.query.filter_by(id=id).first()
            for attr in data:
                setattr(bird, attr, data[attr])
            db.session.add(bird)
            db.session.commit()
            return make_response(bird.to_dict(), 200)
        except Exception as e:
            db.session.rollback()
            return make_response(jsonify({'error': str(e)}), 500)

    def delete(self, id):
        try:
            bird = Bird.query.filter_by(id=id).first()
            db.session.delete(bird)
            db.session.commit()
            return make_response('', 204)
        except Exception as e:
            db.session.rollback()
            return make_response(jsonify({'error': str(e)}), 500)

api.add_resource(BirdByID, '/birds/<int:id>')

if __name__ == "__main__":
    app.run(debug=True)
