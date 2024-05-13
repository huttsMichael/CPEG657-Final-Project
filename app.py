from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient, server_api

app = Flask(__name__)

def read_mongodb_uri():
    with open('mongodb_uri.txt', 'r') as file:
        return file.readline().strip()

def initialize_mongodb():
    uri = read_mongodb_uri()
    client = MongoClient(uri, server_api=server_api.ServerApi('1'))
    db = client['vehicle_data']
    specs_collection = db['specs']
    return specs_collection

specs_collection = initialize_mongodb()

@app.route('/')
def index():
    makes = specs_collection.distinct('make')
    return render_template('index.html', makes=makes)

@app.route('/models/<make>')
def models(make):
    models = specs_collection.find({'make': make}).distinct('model')
    return jsonify(models)

@app.route('/years/<make>/<model>')
def years(make, model):
    years = specs_collection.find({'make': make, 'model': model}).distinct('year')
    return jsonify(sorted(years))

@app.route('/search', methods=['POST'])
def search():
    query = {}
    make = request.form.get('make', '').strip()
    model = request.form.get('model', '').strip()
    year = request.form.get('year', '').strip()

    if make:
        query['make'] = make
    if model:
        query['model'] = model
    if year:
        query['year'] = year  # Year is already confirmed to be stored as a string

    results = list(specs_collection.find(query))
    unique_results = {f"{car['make']}-{car['model']}-{car['year']}": car for car in results}
    final_results = list(unique_results.values())

    return render_template('results.html', cars=final_results)




if __name__ == '__main__':
    app.run(debug=True)
