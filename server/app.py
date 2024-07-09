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
        restaurant = Restaurant.query.filter(Restaurant.id == id).first()

        if not restaurant:
            return make_response(jsonify({"message": "Restaurant not found"}), 404)

        response = make_response(jsonify(restaurant.to_dict()), 200)

        return response
    
    def delete(self, id):
        restaurant = Restaurant.query.filter(Restaurant.id == id).first()

        if restaurant:
        
          db.session.delete(restaurant)
          db.session.commit()
          response = make_response({}, 204)

        else:
          return make_response(jsonify({"error": "Restaurant not found"}), 404)

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

        restaurant_pizza = request.get_json()

        pizza_price = restaurant_pizza.get("price")
        pizza_id = restaurant_pizza.get("pizza_id")
        restaurant_id = restaurant_pizza.get("restaurant_id")

        if not pizza_price or not pizza_id or not restaurant_id:
            return make_response(jsonify({"message": "Missing required fields"}), 400)
        
        if pizza_price < 1 or pizza_price > 30:
            return make_response(jsonify({"message": "Price must be between 1 and 30"}), 400)

        restaurant_pizza = RestaurantPizza(price=pizza_price, pizza_id=pizza_id, restaurant_id=restaurant_id)

        db.session.add(restaurant_pizza)
        db.session.commit()

        response = make_response(jsonify(restaurant_pizza.to_dict()), 201)

        return response
    

api.add_resource(RestaurantPizzas, "/restaurant_pizzas")

if __name__ == "__main__":
    app.run(port=5555, debug=True)
