from flask import Flask, request, jsonify
from input_analyzer import analyze_input
from junction import select_and_process
from output_handler import process_output
from ai_manager import add_ai, update_ai, remove_ai, get_ai, list_ais
import uuid
from flask_cors import CORS
from werkzeug.exceptions import BadRequest, NotFound
import nltk

app = Flask(__name__)
CORS(app)

nltk.download('punkt')
nltk.download('stopwords')



@app.errorhandler(BadRequest)
@app.errorhandler(NotFound)
def handle_error(error):
    return jsonify({'error': str(error)}), error.code


@app.route('/process', methods=['POST'])
def process_request():
    try:
        user_input = request.json['input']
    except KeyError:
        raise BadRequest("Missing 'input' in request JSON")

    analyzed_input = analyze_input(user_input)
    raw_output = select_and_process(analyzed_input)
    final_output = process_output(raw_output)

    return jsonify({'output': final_output})


@app.route('/add_ai', methods=['POST'])
def add_ai_route():
    try:
        data = request.json
        ai_id = add_ai(data['name'], data['type'], data['details'])
        return jsonify({'message': 'AI added successfully', 'id': ai_id})
    except KeyError as e:
        raise BadRequest(f"Missing key in request JSON: {str(e)}")


@app.route('/update_ai', methods=['POST'])
def update_ai_route():
    try:
        data = request.json
        success = update_ai(data['id'], data['details'])
        if success:
            return jsonify({'message': 'AI updated successfully'})
        else:
            raise NotFound('AI not found')
    except KeyError as e:
        raise BadRequest(f"Missing key in request JSON: {str(e)}")


@app.route('/remove_ai', methods=['POST'])
def remove_ai_route():
    try:
        ai_id = request.json['id']
        success = remove_ai(ai_id)
        if success:
            return jsonify({'message': 'AI removed successfully'})
        else:
            raise NotFound('AI not found')
    except KeyError:
        raise BadRequest("Missing 'id' in request JSON")


@app.route('/get_ai', methods=['GET'])
def get_ai_route():
    ai_id = request.args.get('id')
    if not ai_id:
        raise BadRequest("Missing 'id' in query parameters")
    ai = get_ai(ai_id)
    if ai:
        return jsonify({'ai': ai})
    else:
        raise NotFound('AI not found')


@app.route('/list_ais', methods=['GET'])
def list_ais_route():
    ais = list_ais()
    return jsonify({'ais': ais})


if __name__ == '__main__':
    app.run(debug=True)