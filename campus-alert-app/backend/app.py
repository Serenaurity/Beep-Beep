from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import os
from datetime import datetime
import psycopg2
from werkzeug.utils import secure_filename
import redis

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

try:
    redis_client = redis.Redis(host='redis', port=6379, decode_responses=True)
except:
    redis_client = None

def get_db_connection():
    conn = psycopg2.connect(os.getenv('DATABASE_URL'))
    return conn

alerts = []
messages = []

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "Campus Alert API"
    })

@app.route('/api/alerts', methods=['GET'])
def get_alerts():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT * FROM alerts WHERE status = %s ORDER BY created_at DESC', ('active',))
        rows = cur.fetchall()
        cur.close()
        conn.close()
        
        alerts_list = []
        for row in rows:
            alerts_list.append({
                'id': row[0],
                'type': row[1],
                'title': row[2],
                'detail': row[3],
                'lat': float(row[4]),
                'lng': float(row[5]),
                'reporter': row[6],
                'status': row[7],
                'image_url': row[8],
                'time': row[9].strftime('%H:%M') if row[9] else None
            })
        return jsonify(alerts_list)
    except:
        return jsonify(alerts)

@app.route('/api/alerts', methods=['POST'])
def create_alert():
    data = request.json
    
    alert = {
        'type': data.get('type'),
        'title': data.get('title'),
        'detail': data.get('detail'),
        'lat': data.get('lat'),
        'lng': data.get('lng'),
        'reporter': data.get('reporter', 'Anonymous'),
        'status': 'active',
        'time': datetime.now().strftime('%H:%M')
    }
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            'INSERT INTO alerts (type, title, detail, latitude, longitude, reporter, status) VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id',
            (alert['type'], alert['title'], alert['detail'], alert['lat'], alert['lng'], alert['reporter'], alert['status'])
        )
        alert_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()
        
        alert['id'] = alert_id
        socketio.emit('new_alert', alert)
        
        return jsonify(alert), 201
    except Exception as e:
        alerts.append(alert)
        alert['id'] = len(alerts)
        return jsonify(alert), 201

@app.route('/api/messages', methods=['GET'])
def get_messages():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT m.id, u.username, m.message, m.created_at FROM messages m JOIN users u ON m.user_id = u.id ORDER BY m.created_at DESC LIMIT 50')
        rows = cur.fetchall()
        cur.close()
        conn.close()
        
        messages_list = []
        for row in rows:
            messages_list.append({
                'id': row[0],
                'user': row[1],
                'message': row[2],
                'time': row[3].strftime('%H:%M') if row[3] else None
            })
        return jsonify(messages_list)
    except:
        return jsonify(messages)

@socketio.on('send_message')
def handle_message(data):
    message = {
        'id': len(messages) + 1,
        'user': data.get('user', 'Anonymous'),
        'message': data.get('message'),
        'time': datetime.now().strftime('%H:%M')
    }
    messages.append(message)
    emit('new_message', message, broadcast=True)

@socketio.on('connect')
def handle_connect():
    print('Client connected')
    emit('connection_response', {'status': 'connected'})

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=8000, debug=True)
