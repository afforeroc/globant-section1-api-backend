from flask import Flask, request, jsonify
import pandas as pd

app = Flask(__name__)

@app.route('/api/receive_json', methods=['POST'])
def receive_json():
    try:
        # Get the JSON data from the request
        json_data = request.get_json()
        # Convert JSON to DataFrame
        df = pd.DataFrame.from_dict(json_data)
        # You can perform any operations with the DataFrame here
        # Return the DataFrame as JSON (just for demonstration purposes)
        return jsonify(df.to_dict(orient='records'))
    except Exception as e:
        response = {'status': 'error', 'message': str(e)}
        return jsonify(response), 500

if __name__ == '__main__':
    app.run(debug=True)