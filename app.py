from flask import Flask

app = Flask(__name__)

app.config['SECRET_KEY'] = "br0wnthumbs"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

@app.route("/test", methods=["GET"])
def test():
    return ("WORKS")
