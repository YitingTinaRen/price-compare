from flask import *
from flask_cors import CORS
import config
import api

app = None

app = Flask(__name__)
app.config.from_object(config)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
app.register_blueprint(api.api_compare, url_prefix="/")
app.register_blueprint(api.api_member, url_prefix="/")

# Pages


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/compare")
def compare():
    return render_template("compare.html")


@app.route("/member")
def member():
    return render_template("member.html")


app.run(host=config.HOST, port=config.PORT, debug=config.DEBUG)
