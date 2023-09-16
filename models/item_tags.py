from db import db

class ItemTags(db.Model): # Secondary table for many-to-many relationship between items and tags.
    __tablename__ = "item_tags"

    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey("items.id"), nullable=False, unique=False)
    tag_id = db.Column(db.Integer, db.ForeignKey("tags.id"), nullable=False, unique=False)