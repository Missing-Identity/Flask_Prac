from db import db

class StoreModel(db.Model):
    __tablename__ = "stores"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=False, nullable=False)
    items = db.relationship("ItemModel", back_populates="store", lazy="dynamic", cascade="all, delete") # lazy="dynamic" means that the items attribute will be a query builder that has the ability to look into the items table.
    # cascade="all, delete" means that when a store is deleted, all the items that belong to that store will also be deleted.
    tags = db.relationship("TagModel", back_populates="store", lazy="dynamic", cascade="all, delete")