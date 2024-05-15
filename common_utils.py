import csv

def read_vehicle_urls_from_csv(file_path):
    urls = []
    with open(file_path, mode='r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            urls.append((row['URL'], row['Make'], row['Model'], row['Year']))
    return urls
