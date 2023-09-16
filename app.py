import os
from flask import Flask, jsonify
from flask_smorest import Api
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from db import db
from blocklist import BLOCKLIST
import models
from resources.item import blp as ItemBlueprint
from resources.store import blp as StoreBlueprint
from resources.tag import blp as TagBlueprint
from resources.user import blp as UserBlueprint


def create_app(db_url=None):
    app = Flask(__name__)
    app.config.update(
        PROPAGATE_EXCEPTIONS=True,
        API_TITLE='Stores REST API',
        API_VERSION='1.0.0',
        OPENAPI_VERSION='3.0.3',
        OPENAPI_URL_PREFIX='/',
        OPENAPI_SWAGGER_UI_PATH='/swagger-ui',
        OPENAPI_SWAGGER_UI_URL='https://cdn.jsdelivr.net/npm/swagger-ui-dist/',
        SQLALCHEMY_DATABASE_URI=db_url or os.getenv(
            'DATABASE_URL', 'sqlite:///data.db'),
        SQLALCHEMY_TRACK_MODIFICATIONS=False
    )
    db.init_app(app)
    migrate = Migrate(app, db)  # This is used to migrate the database
    api = Api(app)
    app.config["JWT_SECRET_KEY"] = "13523012552725194602293233160327692629"
    jwt = JWTManager(app)

    # This function is called when the token is in the blocklist.
    @jwt.token_in_blocklist_loader
    # jwt_header and jwt_payload are the headers and payload of the expired token
    def check_if_token_in_blocklist(jwt_header, jwt_payload):
        # jti is "JWT ID", a unique identifier for a JWT. It is used to identify the JWT. It is not sensitive. It is used to prevent the JWT from being replayed. It is a UUID4 string.
        return jwt_payload["jti"] in BLOCKLIST

    # This function is called when the token is revoked. Called when BLOCKLIST sends error.
    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        return (jsonify({"message": "The token has been revoked", "error": "token_revoked"}), 401)

    # This function is called when a fresh token is required but a non fresh token is sent.
    @jwt.needs_fresh_token_loader
    def token_not_fresh_callback(jwt_header, jwt_payload):
        return (jsonify({"message": "The token is not fresh", "error": "fresh_token_required"}), 401)

    # This adds additional claims to the JWT token used to see if user is admin, etc.
    @jwt.additional_claims_loader
    # identity is what we define when creating the access token
    def add_claims_to_jwt(identity):
        if identity == 1:  # If the user is admin
            return {"is_admin": True}
        return {"is_admin": False}

    @jwt.expired_token_loader  # This function is called when the token has expired
    # jwt_header and jwt_payload are the headers and payload of the expired token
    def expired_token_callback(jwt_header, jwt_payload):
        return (jsonify({"message": "The token has expired", "error": "token_expired"}), 401)

    @jwt.invalid_token_loader  # This function is called when the token is invalid
    def invalid_token_callback(error):
        return (jsonify({"message": "Signature verification failed", "error": "invalid_token"}), 401)

    # This function is called when a token is not present in the request
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return (jsonify({"message": "Request does not contain an access token", "error": "authorization_required"}), 401)

    # with app.app_context():
    #     db.create_all()
    api.register_blueprint(ItemBlueprint)
    api.register_blueprint(StoreBlueprint)
    api.register_blueprint(TagBlueprint)
    api.register_blueprint(UserBlueprint)
    return app
