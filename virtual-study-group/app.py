from flask import Flask
from flask_migrate import Migrate
from models import db, User
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from config import Config
from flask_mail import Mail
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
from flask_uploads import UploadSet, configure_uploads, IMAGES, DOCUMENTS, TEXT


# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)


# Initialize extensions
db.init_app(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
mail = Mail(app)
load_dotenv()  # Automatically loads .env file
files = UploadSet('files')
configure_uploads(app, files)

# User loader for Flask-Login
from models.user import User

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Register blueprints
from routes.auth import auth_bp
from routes.chat import chat_bp
from routes.home import home_bp
from routes.groups import groups_bp


app.register_blueprint(auth_bp)
app.register_blueprint(chat_bp)
app.register_blueprint(home_bp)
app.register_blueprint(groups_bp)


@app.route('/routes', methods=['GET'])
def list_routes():
    routes = []
    for rule in app.url_map.iter_rules():
        # Skip routes that start with `_` or related to static files
        if not rule.rule.startswith('/static'):
            routes.append({
                "endpoint": rule.endpoint,
                "methods": list(rule.methods - {'HEAD', 'OPTIONS'}),
                "url": rule.rule
            })

    # Sort routes alphabetically by URL
    routes.sort(key=lambda x: x["url"])

    return {
        "routes": routes
    }, 200


# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    return "Page Not Found", 404
