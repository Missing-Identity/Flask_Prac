from flask.views import MethodView
from flask_smorest import abort, Blueprint
from passlib.hash import pbkdf2_sha256
from flask_jwt_extended import create_access_token, get_jwt, jwt_required, create_refresh_token, get_jwt_identity

from blocklist import BLOCKLIST
from db import db
from models import UserModel
from schemas import UserSchema

blp = Blueprint("users", __name__, description="Operations on users")

@blp.route("/register")
class UserRegister(MethodView):
    @blp.arguments(UserSchema)
    def post(self, user_data): # user_data(call it whatever) is the data that is passed in the request body. It contains the validated fields as JSON.
        if UserModel.query.filter_by(username=user_data["username"]).first(): # Checks if the username already exists
            abort(500, message="Username already exists")
        user = UserModel( # Create a new user
            username=user_data["username"],
            password=pbkdf2_sha256.hash(user_data["password"])
        )
        db.session.add(user)
        db.session.commit()
        return {"message": "User created"}, 201
    
@blp.route("/login")
class UserLogin(MethodView):
    @blp.arguments(UserSchema)
    def post(self, user_data): # user_data(call it whatever) is the data that is passed in the request body. It contains the validated fields as JSON.
        user = UserModel.query.filter_by(username=user_data["username"]).first() # Get the user from the database
        if user and pbkdf2_sha256.verify(user_data["password"], user.password): # If the user exists and the password is correct after hashing
            access_token = create_access_token(identity=user.id, fresh=True) # Create an access token, fresh=True means that the user has logged in with a valid username and password
            refresh_token = create_refresh_token(identity=user.id) # Create a refresh token
            return {"access_token": access_token, "refresh_token": refresh_token}, 200
        abort(401, message="Invalid username or password")

@blp.route("/refresh")
class UserRefresh(MethodView):
    @jwt_required(refresh=True) # This is a decorator that requires a JWT token to access the view. Basically it requires the user to be logged in with a valid refresh token
    def post(self):
        current_user = get_jwt_identity() # Get the user id from the JWT token
        new_token = create_access_token(identity=current_user, fresh=False) # Create a new access token. fresh=False prevents the user from accessing fresh=True views
        jti = get_jwt()["jti"] # Get the jti from the JWT token
        BLOCKLIST.add(jti) # Add the jti to the blocklist. Gets new non fresh token once the old one expires.
        return {"access_token": new_token}, 200



@blp.route("/logout")
class UserLogout(MethodView): # This class is used to logout the user
    @jwt_required() # This is a decorator that requires a JWT token to access the view. Basically it requires the user to be logged in with a valid access token
    def post(self):
        jti = get_jwt()["jti"] # Get the jti from the JWT token
        BLOCKLIST.add(jti) # Add the jti to the blocklist
        return {"message": "Successfully logged out"}, 200
    
@blp.route("/user/<int:user_id>")
class User(MethodView):
    @blp.response(200, UserSchema)
    def get(self, user_id): # Get the user from the database
        user = UserModel.query.get_or_404(user_id)
        return user
    
    def delete(self, user_id): # Delete the user from the database
        user = UserModel.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        return {"message": "User deleted"}, 200