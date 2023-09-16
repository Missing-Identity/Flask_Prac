from marshmallow import Schema, fields

class PlainItemSchema(Schema):
    id = fields.Int(dump_only=True) # dump_only means that this field will only be used for dumping data back to the user. It will not be used for loading data
    name = fields.Str(required=True) # required means that this field is required for loading data 
    price = fields.Float(required=True)

class PlainStoreSchema(Schema):
    id = fields.Int(dump_only=True) 
    name = fields.Str(required=True)

class PlainTagSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)

class ItemUpdateSchema(Schema):
    name = fields.Str()
    price = fields.Float()
    store_id = fields.Int() # Need id here if our put request needs to update the store_id for creating a new item.

class ItemSchema(PlainItemSchema):
    store_id = fields.Int(required=True, load_only=True)
    store = fields.Nested(PlainStoreSchema(), dump_only=True) # Nested means that the store attribute will be nested inside the item attribute in the response body.
    tags = fields.List(fields.Nested(PlainTagSchema()), dump_only=True) # List of Nested tags means that the tags attribute will be a list of tags that are nested inside the item attribute in the response body.

class StoreSchema(PlainStoreSchema):
    items = fields.List(fields.Nested(PlainItemSchema(), dump_only=True)) # many=True means that the items attribute will be a list of items. dump_only=True means that the items attribute will only be used for dumping data back to the user. It will not be used for loading data.
    tags = fields.List(fields.Nested(PlainTagSchema(), dump_only=True))

class TagSchema(PlainTagSchema):
    store_id = fields.Int(load_only=True)
    store = fields.Nested(PlainStoreSchema(), dump_only=True)
    items = fields.List(fields.Nested(PlainItemSchema(), dump_only=True))
    
class ItemTagSchema(Schema):
    message = fields.Str()
    item = fields.Nested(ItemSchema())
    tag = fields.Nested(TagSchema())

class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    username = fields.Str(required=True)
    password = fields.Str(required=True, load_only=True) # For passwords load_only is compulsory. This means that the password will not be dumped back to the user.