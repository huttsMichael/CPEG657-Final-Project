from pymongo import MongoClient, UpdateOne
from pymongo.server_api import ServerApi

def read_mongodb_uri():
    with open('mongodb_uri.txt', 'r') as file:
        return file.readline().strip()

def initialize_mongodb():
    uri = read_mongodb_uri()
    client = MongoClient(uri, server_api=ServerApi('1'))
    db = client['vehicle_data']
    specs_collection = db['specs_improved']
    error_collection = db['errors']
    return specs_collection, error_collection
