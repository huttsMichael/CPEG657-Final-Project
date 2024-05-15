from flask import Flask, jsonify, request, render_template
from pymongo import MongoClient
import pymongo
from bson import ObjectId
import json

app = Flask(__name__)

# Custom JSON Encoder
class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        # Add more checks for other types like datetime if necessary
        return json.JSONEncoder.default(self, obj)

# Apply the custom JSON Encoder for the Flask app
app.json_encoder = CustomJSONEncoder

# Helper function to read MongoDB URI
def read_mongodb_uri():
    with open('mongodb_uri.txt', 'r') as file:
        return file.readline().strip()

# Initialize MongoDB
def initialize_mongodb():
    uri = read_mongodb_uri()
    client = MongoClient(uri)
    db = client['vehicle_data']
    return db['specs']

specs_collection = initialize_mongodb()

@app.route('/')
def index():
    return render_template('index.html')

def clean_column_name(name):
    """ Simplifies column names for JavaScript compatibility """
    return name.replace(' ', '_').replace('(', '').replace(')', '').replace('-', '_')

@app.route('/fetch_data', methods=['GET', 'POST'])
def fetch_data():
    try:
        draw = int(request.args.get('draw', 1))
        start = int(request.args.get('start', 0))
        length = int(request.args.get('length', 10))
        sort_column_index = request.args.get('order[0][column]')
        sort_direction = request.args.get('order[0][dir]', 'asc')
        
        # Determine the column name to sort by
        sort_column_name = request.args.get(f'columns[{sort_column_index}][data]', 'make')
        
        # Logging to debug
        print(f"Sorting by {sort_column_name} {sort_direction}")

        # Apply sorting in MongoDB query
        sort_order = pymongo.ASCENDING if sort_direction == 'asc' else pymongo.DESCENDING
        data = list(specs_collection.find({}, {'_id': False})
                    .sort(sort_column_name, sort_order)
                    .skip(start).limit(length))

        total_count = specs_collection.count_documents({})
        clean_data = [{clean_column_name(k): v for k, v in item.items()} for item in data]

        response = {
            "draw": draw,
            "recordsTotal": total_count,
            "recordsFiltered": total_count,
            "data": clean_data
        }
        return jsonify(response)
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"error": str(e)}), 500



@app.route('/column_names')
def column_names():
    sample_doc = specs_collection.find_one()
    if sample_doc:
        # Prioritize certain columns and push 'url' to last
        priority_columns = ['make', 'model', 'year']
        last_columns = ['url']
        other_columns = [k for k in sample_doc.keys() if k not in priority_columns + last_columns and k != '_id']

        # Order columns: priority, others, last
        ordered_columns = priority_columns + other_columns + last_columns
        columns = [{'data': clean_column_name(k), 'title': k} for k in ordered_columns]
        return jsonify({'columns': columns})
    else:
        return jsonify({'error': 'No data available'})




if __name__ == '__main__':
    app.run(debug=True)
