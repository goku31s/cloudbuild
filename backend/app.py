import logging
import os
from flask import Flask, jsonify
from flask_cors import CORS
import pymongo
from pymongo.errors import ConnectionFailure
import time

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

logger.debug("Starting import of Flask")
app = Flask(__name__)
CORS(app)
logger.debug("Flask app created and CORS configured")

def connect_to_mongodb():
    mongo_host = os.getenv('MONGO_HOST', 'mongodb-service')
    mongo_port = os.getenv('MONGO_PORT', '27017')
    mongo_uri = f"mongodb://{mongo_host}:{mongo_port}/"
    
    retry_count = 30
    while retry_count > 0:
        try:
            logger.info(f"Attempting to connect to MongoDB at {mongo_uri}")
            client = pymongo.MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
            client.server_info()  # Will raise an exception if unable to connect
            db = client["messagedb"]
            collection = db["messages"]
            logger.info("Successfully connected to MongoDB")
            return collection
        except ConnectionFailure as e:
            logger.error(f"Connection to MongoDB failed: {str(e)}")
            retry_count -= 1
            time.sleep(2)  # Wait for 2 seconds before retrying

    raise Exception("Failed to connect to MongoDB after retries")

@app.route('/healthz')
def health_check():
    return jsonify({"status": "healthy"}), 200

@app.route('/message')
def get_message():
    try:
        collection = connect_to_mongodb()
        message = collection.find_one({})
        if message and "text" in message:
            return jsonify({"message": message["text"]})
        else:
            return jsonify({"message": "No Meaasage Found"})
    except Exception as e:
        logger.error(f"Error retrieving message: {str(e)}")
        return jsonify({"message": "Server Not Built"})

if __name__ == '__main__':
    logger.info("Starting the Flask application")
    app.run(host='0.0.0.0', port=5000)
