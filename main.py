import queryKnowledgeBase
import assetUpload
from flask import Flask, request, render_template
from flask_cors import CORS

app = Flask(__name__, static_folder='static')  # Specify the 'static' folder for static files
CORS(app)


@app.route("/", methods=['GET'])
def index():
    return render_template("index.html")

@app.route("/chat", methods=['POST'])
def hello():
    data = request.json
    message = data.get('message')
    answer = queryKnowledgeBase.ask_question(message)
    res_obj = {'message': answer}
    return res_obj


# app.run(host='localhost', port=5000)
if __name__ == '__main__':
    app.run(port=5001)

