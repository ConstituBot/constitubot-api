from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/chatbot', methods=['POST'])
def chatbot():
    data = request.get_json()
    user_message = data.get("message", "")
    ai_response = f"Você disse: {user_message}"
    return jsonify({"response": ai_response})

if __name__ == '__main__':
    app.run()

