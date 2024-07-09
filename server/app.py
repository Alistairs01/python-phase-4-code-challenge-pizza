#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response,jsonify
from flask_restful import Api, Resource
from models import db, Restaurant, RestaurantPizza, Pizza
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)


@app.route("/")
def index():
    return "<h1>Code challenge</h1>"



class Restaurants(Resource):

    def get(self):

        restaurants = Restaurant.query.all()

        if not restaurants:
            return make_response(jsonify({"message": "No restaurants found"}), 404)

        restaurant_dict = [restaurant.to_dict(only = ("address", "id", "name")) for restaurant in restaurants]
        response = make_response(jsonify(restaurant_dict), 200)

        return response
api.add_resource(Restaurants, "/restaurants")

class RestaurantsId(Resource):
    def get(self, id):
        restaurant = Restaurant.query.filter_by(id = id).first()

        if restaurant:
            response = make_response(jsonify(restaurant.to_dict()), 200)
        else:
            response = make_response(jsonify({"error": "Restaurant not found"}), 404)
            

        return response
    
    def delete(self, id):
        restaurant = Restaurant.query.filter(Restaurant.id == id).first()

        if restaurant:
            db.session.delete(restaurant)
            db.session.commit()
            response = make_response({}, 204)

        else:
            response = make_response(jsonify({"error": "Restaurant not found"}), 404)

        return response
        
        
api.add_resource(RestaurantsId, "/restaurants/<int:id>")


class Pizzas(Resource):

    def get(self):

        pizzas = Pizza.query.all()

        if not pizzas:
            return make_response(jsonify({"message": "No pizzas found"}), 404)

        pizza_dict = [pizza.to_dict(only = ("id", "name", "ingredients")) for pizza in pizzas]
        response = make_response(jsonify(pizza_dict), 200)

        return response
    
api.add_resource(Pizzas, "/pizzas")
    
class RestaurantPizzas(Resource):
    
    def post(self):
       
        restaurant_pizza_data = request.get_json()
        try:
            price = restaurant_pizza_data.get('price')
            pizza_id = restaurant_pizza_data.get('pizza_id')
            restaurant_id = restaurant_pizza_data.get('restaurant_id')
            # added validation
            if price < 1 or price > 30:
                return make_response(jsonify({"errors": ["validation errors"]}), 400)
        

            restaurant_pizza = RestaurantPizza(price=price, pizza_id=pizza_id, restaurant_id=restaurant_id)
        
            db.session.add(restaurant_pizza)
            db.session.commit()

            response_dict = restaurant_pizza.to_dict()
            return make_response(
            jsonify(response_dict),
            201
            )

        except KeyError as e:
            db.session.rollback()
            return make_response(jsonify({"errors": [f"Missing key: {str(e)}"]}), 404)
        finally:
            db.session.close()

api.add_resource(RestaurantPizzas, '/restaurant_pizzas')

if __name__ == "__main__":
    app.run(port=5555, debug=True)
