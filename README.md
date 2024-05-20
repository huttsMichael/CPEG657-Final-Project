# Automobile Data Aggregator

## Dependencies
- Python 3.10.8
- Selenium 4.19.0
- Undetected ChromeDriver 3.5.5
- Fake UserAgent 1.5.1
- Flask 3.0.3
- PyMongo 4.6.3


## Setup and Usage
### MongoDB
If you want to skip scraping, a full dump is availible in the dump/ folder. Simply import that into MongoDB and it should work. Then add your own mongouri to mongo_creds.txt and all code should work.

### Scraping
Run `scrape.py`. DB updating and rechecking is configured in main.

### Flask
Run `app.py` No configuration should be needed if MongoDB was setup correctly in previous steps.

