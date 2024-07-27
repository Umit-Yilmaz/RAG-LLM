from flask import Flask, request, jsonify
import subprocess
from flask_cors import CORS

app = Flask(__name__, static_folder='static')
CORS(app)  

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/query', methods=['POST'])
def query():
    query_text = request.json.get('query')
    # Komut çalıştırma
    result = subprocess.run(['python', 'ask.py', query_text], capture_output=True, text=True)
    response_text = result.stdout
    return jsonify({'response': response_text})

if __name__ == "__main__":
    app.run(port=5000)  # Port numarasını kontrol edin
    
# author: Umit-Yilmaz
