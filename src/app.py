from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/api/agent', methods=['POST'])
def ai_agent():
    data = request.json
    # Process the input data and generate a response
    response = {
        'status': 'success',
        'message': 'AI Agent processed the request successfully.',
        'data': data  # Echoing back the input data for demonstration
    }
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)