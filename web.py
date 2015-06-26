from flask import Flask, render_template, request
from config import CLINICAL

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html') 


@app.route('/fhir-app/launch.html')
def launch():
    return render_template(
            'launch.html',
            client_id=CLINICAL['client_id'],
            scope=' '.join(CLINICAL['scopes']),
            redirect_uri=CLINICAL['redirect_uri']) 


if __name__ == '__main__':
    app.run(port=8000, debug=True)
