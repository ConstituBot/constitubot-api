# app.py

from flask import Flask, request, jsonify
from flask_cors import CORS
import asyncio
from inference.inference import get_answer_from_bot
app = Flask(__name__)
CORS(app)

@app.route('/chatbot', methods=['POST'])
def chatbot():
    data = request.get_json()
    user_message = data.get("message", "")

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    answer = loop.run_until_complete(get_answer_from_bot(user_message))

    return jsonify({"response": answer})

if __name__ == '__main__':
    app.run()
