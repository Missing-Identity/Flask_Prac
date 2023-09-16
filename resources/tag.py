from flask.views import MethodView
from flask_smorest import abort, Blueprint
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from db import db
from models import StoreModel, TagModel, ItemModel
from schemas import TagSchema, ItemTagSchema

blp = Blueprint("tags", __name__, description="Operations on tags")

@blp.route("/item/<int:item_id>/tag/<int:tag_id>")
class LinkTagstoItem(MethodView): # This class is used to link tags to items
    @blp.response(200, TagSchema)
    def post(self, item_id, tag_id):
        item = ItemModel.query.get_or_404(item_id)
        tag = TagModel.query.get_or_404(tag_id)
        try:
            item.tags.append(tag) # Add the tag to the item
            db.session.add(item)
            db.session.commit()
        except SQLAlchemyError as e:
            abort(500, message=str(e))
        return tag
    
    @blp.response(200, ItemTagSchema)
    def delete(self, item_id, tag_id):
        item = ItemModel.query.get_or_404(item_id)
        tag = TagModel.query.get_or_404(tag_id)
        try:
            item.tags.remove(tag) # Remove the tag from the item
            db.session.add(item)
            db.session.commit()
        except SQLAlchemyError as e:
            abort(500, message=str(e))
        return {"message": "Tag removed from item"}

@blp.route("/store/<int:store_id>/tag")
class TabInStore(MethodView):
    @blp.response(200, TagSchema(many=True))
    def get(self, store_id):
        store = StoreModel.query.get_or_404(store_id)
        return store.tags.all() # Get all the tags that belong to the store

    @blp.arguments(TagSchema)
    @blp.response(201, TagSchema)
    def post(self, tag_data, store_id):
        # Below Line only needed if our tag names were not defined as unique in the database
        #if TagModel.query.filter_by(TagModel.store_id == store_id, TagModel.name == tag_data["name"]).first(): # Checks if the tag already exists in the store
            #abort(500, message="Tag already exists") # If the tag already exists, then abort.
        tag = TagModel(**tag_data, store_id=store_id)
        try:
            db.session.add(tag)
            db.session.commit()
        except SQLAlchemyError as e:
            abort(500, message=str(e))
        return tag
    
@blp.route("/tag/<int:tag_id>")
class Tag(MethodView):
    @blp.response(200, TagSchema)
    def get(self, tag_id):
        tag = TagModel.query.get_or_404(tag_id)
        return tag
    
    @blp.response(202, description="Deletes a tag if it is not linked to any items", example={"message": "Tag deleted"})
    @blp.alt_response(404, description="Tag not found", example={"message": "Tag not found"})
    @blp.alt_response(400, description="Returned if the tag is linked to an item", example={"message": "Tag is linked to an item and cannot be deleted"})
    def delete(self, tag_id):
        tag = TagModel.query.get_or_404(tag_id)
        if not tag.items:
            db.session.delete(tag)
            db.session.commit()
            return {"message": "Tag deleted"}
        abort(400, message="Tag is linked to an item and cannot be deleted")