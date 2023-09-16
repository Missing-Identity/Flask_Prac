from flask import request
from flask.views import MethodView
from flask_smorest import abort, Blueprint
from flask_jwt_extended import jwt_required, get_jwt
from sqlalchemy.exc import SQLAlchemyError

from db import db

from models import ItemModel
from schemas import ItemSchema, ItemUpdateSchema

blp = Blueprint("items", __name__, description="Operations on items")

@blp.route("/item")
class ItemList(MethodView):
    @blp.response(200, ItemSchema(many=True)) # many=True means that the response body will be a list of items
    def get(self):
        return ItemModel.query.all() # Get all the items from the database
    
    # We need to keep Authorization in Headers and not in the body
    @jwt_required() # This is a decorator that requires a JWT token to access the view. Basically it requires the user to be logged in with a valid access token
    @blp.arguments(ItemSchema) # This is a decorator that adds a request body parser to the view. The argument is the schema to use for the request body.
    @blp.response(201, ItemSchema)
    def post(self, item_data): # item_data(call it whatever) is the data that is passed in the request body. It contains the validated fields as JSON.
        jwt = get_jwt()
        if not jwt.get("is_admin"): # If the user is not an admin, then abort with a 401 error.
            abort(401, message="Admin privilege required")
        item = ItemModel(**item_data)
        try:
            db.session.add(item) # Add the item to the database
            db.session.commit() # Commit the changes to the database
        except SQLAlchemyError: # If there is an error, then rollback the changes
            abort(500, message="Could not add item to database")

        return item, 201
    
@blp.route("/item/<int:item_id>")
class Item(MethodView):
    @blp.response(200, ItemSchema) # This is a decorator that adds a response to the spec. The first argument is the status code and the second argument is the schema to use for the response body.
    def get(self, item_id):
        item = ItemModel.query.get_or_404(item_id) # Get the item from the database. If it does not exist, then abort with a 404 error.
        return item
    
    @jwt_required()
    def delete(self, item_id):
        # using jwt additional claims
        jwt = get_jwt()
        if not jwt.get("is_admin"): # If the user is not an admin, then abort with a 401 error.
            abort(401, message="Admin privilege required")
        item = ItemModel.query.get_or_404(item_id)
        db.session.delete(item)
        db.session.commit()
        return {"message": "Item deleted"}
    
    @jwt_required()
    @blp.arguments(ItemUpdateSchema)
    @blp.response(200, ItemSchema) # Order of decorators matters
    def put(self, item_data, item_id): # item_data is before all other arguments.
        jwt = get_jwt()
        if not jwt.get("is_admin"): # If the user is not an admin, then abort with a 401 error.
            abort(401, message="Admin privilege required")
        item = ItemModel.query.get(item_id)
        if item:
            item.price = item_data["price"]
            item.name = item_data["name"]
        else:
            item = ItemModel(id=item_id, **item_data)
        db.session.add(item)
        db.session.commit()
        return item