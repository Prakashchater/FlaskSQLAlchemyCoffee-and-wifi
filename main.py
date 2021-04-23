from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
import requests
import random
app = Flask(__name__)

##Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


##Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)

    def to_dict(self):
        dictionary = {}

        for col in self.__table__.columns:
            dictionary[col.name] = getattr(self, col.name)
        return dictionary

        # Method 2. Altenatively use Dictionary Comprehension to do the same thing.
        # return {col.name: getattr(self, col.name) for col in self.__tabel__.columns }

@app.route("/")
def home():
    return render_template("index.html")


@app.route('/random')
def get_random_cafe():
    cafes = db.session.query(Cafe).all()
    random_cafe = random.choice(cafes)
    return jsonify(cafe=random_cafe.to_dict())

@app.route('/all')
def get_all_cafes():
    cafes = db.session.query(Cafe).all()
    caf = []
    for cafe in cafes:
        caf.append(cafe.to_dict())
    return jsonify(caf)

    # return jsonify(cafes=[cafe.to_dict() for cafe in cafes])

@app.route("/search")
def get_location():
    locations = request.args.get("loc")
    cafe = db.session.query(Cafe).filter_by(location=locations).first()
    if cafe:
        return jsonify(cafe=cafe.to_dict())
    else:
        return jsonify(error={
            "Not Found": "Sorry, we don't have a cafe at that location."})

## HTTP GET - Read Record
# @app.route('/random')
# def get_random_cafe():
#     cafes = db.session.query(Cafe).all()
#     random_cafe = random.choice(cafes)
#     ##Turning SQLAlchemy object into JSON which is called Serialisation.
#     return jsonify(cafe={
#         "id": random_cafe.id,
#         "name": random_cafe.name,
#         "map_url": random_cafe.map_url,
#         "img_url": random_cafe.img_url,
#         "location": random_cafe.location,
#         "seats": random_cafe.seats,
#         "has_toilet": random_cafe.has_toilet,
#         "has_wifi": random_cafe.has_wifi,
#         "has_sockets": random_cafe.has_sockets,
#         "can_take_calls": random_cafe.can_take_calls,
#         "coffee_price": random_cafe.coffee_price,
#     })

## HTTP POST - Create Record

@app.route("/add",methods=["POST"])
def add_cafes():
    new_cafe = Cafe(
        name=request.form.get("name"),
        map_url=request.form.get("map_url"),
        img_url=bool(request.form.get("img_url")),
        location=bool(request.form.get("loc")),
        seats=bool(request.form.get("seats")),
        has_toilet=bool(request.form.get("toilet")),
        has_wifi=bool(request.form.get("wifi")),
        has_sockets=bool(request.form.get("sockets")),
        can_take_calls=bool(request.form.get("calls")),
        coffee_price=request.form.get("coffee_price"),
    )

    db.session.add(new_cafe)
    db.session.commit()

    return jsonify(response={
        "success": "Successfully added the new cafe."
    })

## HTTP PUT/PATCH - Update Record
@app.route("/update-price/<int:id>", methods=["PATCH"])
def update_price(id):
    new_price = request.args.get("new_price")
    cafe = db.session.query(Cafe).get(id)
    if cafe:
        cafe.coffee_price = new_price
        db.session.commit()
        return jsonify(response={"success": "Successfully updated the price."}), 200
    else:
        return jsonify(error={"Not_found": "Sorry a cafe with tha id was not found in the database."}), 400


## HTTP DELETE - Delete Record
@app.route("/reported-close/<int:id>", methods=["DELETE"])
def close(id):
    api_key = request.args.get("api-key")
    if api_key == "YOUR API KEY":
        cafe = db.session.query(Cafe).get(id)
        if cafe:
            db.session.delete(cafe)
            db.session.commit()
            return jsonify(response={"success": "Successfully deleted the cafe from the database."}), 200
        else:
            return jsonify(error={"Not Found": "Sorry a cafe with that id was not found in the database."}), 404
    else:
        return jsonify(error={"Forbidden": "Sorry, that's not allowed. Make sure you have the correct api key."}), 403

if __name__ == '__main__':
    app.run(debug=True)
