from flask import Flask, request, jsonify
from pymongo import MongoClient
from decouple import config
from datetime import datetime
import os
from functools import wraps

app = Flask(__name__)

# Configuration with fallbacks for Railway
try:
    MONGO_URI = config('MONGO_URI')
    API_KEY = config('API_KEY')
except Exception as e:
    print(f"Configuration error: {e}")
    # Fallback values for Railway deployment
    MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://localhost:27017')
    API_KEY = os.environ.get('API_KEY', 'ROYALGUARDAPIKEY-1223424PRODREADY2323784237283487')

# MongoDB setup with error handling
try:
    client = MongoClient(MONGO_URI)
    db = client.royalguard
    activity_collection = db.activity
    print("MongoDB connection established successfully")
except Exception as e:
    print(f"MongoDB connection failed: {e}")
    client = None
    db = None
    activity_collection = None

# API Key authentication decorator
def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if not api_key or api_key != API_KEY:
            return jsonify({'status': 'error', 'message': 'Invalid or missing API key'}), 401
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def health_check():
    try:
        # Test MongoDB connection
        if activity_collection is not None:
            activity_collection.find_one()
            db_status = "connected"
        else:
            db_status = "disconnected"
        
        return jsonify({
            'status': 'healthy', 
            'service': 'Royal Guard Activity API',
            'database': db_status,
            'api_key_configured': bool(API_KEY)
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'database': 'error'
        }), 500

@app.route('/update_activity', methods=['POST'])
def update_activity():
    data = request.get_json()
    if not data or 'user_id' not in data or 'activity_minutes' not in data:
        return jsonify({'status': 'error', 'message': 'Invalid data'}), 400

    # Check API key from request body (for Roblox compatibility)
    api_key_from_body = data.get('api_key')
    api_key_from_header = request.headers.get('X-API-Key')
    
    # Debug logging
    print(f"API Key from body: {api_key_from_body}")
    print(f"API Key from header: {api_key_from_header}")
    print(f"Expected API Key: {API_KEY}")
    
    if not (api_key_from_body == API_KEY or api_key_from_header == API_KEY):
        return jsonify({'status': 'error', 'message': 'Invalid or missing API key'}), 401

    user_id = data['user_id']
    activity_minutes = data['activity_minutes']

    if activity_collection is None:
        return jsonify({'status': 'error', 'message': 'Database not available'}), 503
    
    try:
        activity_collection.update_one(
            {'_id': user_id},
            {'$inc': {'total_activity': activity_minutes}},
            upsert=True
        )
        return jsonify({'status': 'success'}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/log_event', methods=['POST'])
def log_event():
    try:
        # Get API key from headers or request body
        api_key = request.headers.get('X-API-Key') or request.json.get('api_key')
        
        if not api_key or api_key != API_KEY:
            print(f"DEBUG: Invalid API key provided: {api_key}")
            return jsonify({'error': 'Invalid API key'}), 401
        
        data = request.json
        log_type = data.get('log_type')
        log_data = data.get('log_data')
        timestamp = data.get('timestamp')
        
        if not log_type or not log_data:
            return jsonify({'error': 'Missing log_type or log_data'}), 400
        
        # Check for duplicate logs before inserting
        existing_log = db.roblox_logs.find_one({
            'log_type': log_type,
            'log_data.message': log_data.get('message'),
            'log_data.username': log_data.get('username'),
            'timestamp': timestamp
        })
        
        if existing_log:
            print(f"DEBUG: Duplicate log detected, skipping insertion for {log_type}")
            return jsonify({'success': True, 'message': 'Duplicate log ignored'})
        
        # Store log in database for Discord bot to process
        log_entry = {
            'log_type': log_type,
            'log_data': log_data,
            'timestamp': timestamp,
            'processed': False,
            'created_at': datetime.utcnow()
        }
        
        db.roblox_logs.insert_one(log_entry)
        print(f"DEBUG: Stored {log_type} log for processing")
        
        return jsonify({'success': True, 'message': 'Log stored for processing'})
    
    except Exception as e:
        print(f"ERROR in log_event: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
