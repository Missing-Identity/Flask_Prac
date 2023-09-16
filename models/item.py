from db import db


# Mapping between a row in a table to a Python object.
class ItemModel(db.Model):
    # SQLAlchemy will create a table called items if it doesn't exist for this model.
    __tablename__ = "items"

    id = db.Column(db.Integer, primary_key=True)
    # unique=False means that the name of the item need not be unique. nullable=False means that the name of the item cannot be null.
    name = db.Column(db.String(80), unique=False, nullable=False)
    description = db.Column(db.String(80), unique=False, nullable=True)
    # precision=2 means that the price will have 2 decimal places.
    price = db.Column(db.Float(precision=2), unique=False, nullable=False)
    # ForeignKey("stores.id") means that the store_id column is a foreign key that references the id column in the stores table.
    store_id = db.Column(db.Integer, db.ForeignKey(
        "stores.id"), nullable=False, unique=False)
    # This is a relationship between the ItemModel and the StoreModel. back_populates="items" means that the items attribute in the StoreModel will be used to find the items that belong to a store.
    store = db.relationship("StoreModel", back_populates="items")
    # secondary="item_tags" means that the item_tags table will be used to find the tags that belong to an item.
    tags = db.relationship("TagModel", secondary="item_tags",
                           back_populates="items", lazy="dynamic", cascade="all, delete")
