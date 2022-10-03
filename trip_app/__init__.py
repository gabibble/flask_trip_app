from flask import Flask
from trip_app.site.routes import site
from .api.routes import api
from config import Config


from flask_migrate import Migrate
from .models import db as root_db, ma #login_manager

from flask_cors import CORS
from .helpers import JSONEncoder

app = Flask(__name__)

app.register_blueprint(site)
app.register_blueprint(api)
app.config.from_object(Config)

root_db.init_app(app)

migrate = Migrate(app, root_db)

# login_manager.init_app(app)
# login_manager.login_view = 'auth.login' #named login in this app, used signin in other projects

ma.init_app(app)

# #day3
app.json_encoder = JSONEncoder
CORS(app)