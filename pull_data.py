from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

def read_mongodb_uri():
    # Reads the MongoDB URI from a local file
    with open('mongodb_uri.txt', 'r') as file:
        return file.readline().strip()

def initialize_mongodb():
    # Initializes MongoDB connection and returns the collections
    uri = read_mongodb_uri()
    client = MongoClient(uri, server_api=ServerApi('1'))
    db = client['vehicle_data']
    specs_collection = db['specs']
    error_collection = db['errors']
    return specs_collection, error_collection

def fetch_sample_data(collection, limit=3):
    # Fetches a limited number of documents from a given MongoDB collection to serve as a sample
    return list(collection.find().limit(limit))

def main():
    specs_collection, error_collection = initialize_mongodb()

    # Fetch sample data from 'specs' collection
    specs_sample = fetch_sample_data(specs_collection)

    print("Sample Vehicle Specs Data:")
    for data in specs_sample:
        print(data)

if __name__ == "__main__":
    main()
