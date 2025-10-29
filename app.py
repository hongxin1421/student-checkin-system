from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import json
import os
from datetime import datetime
import threading

app = Flask(__name__)
CORS(app)

# 数据文件路径
DATA_FILE = 'checkin_data.json'
IP_RECORDS_FILE = 'ip_records.json'

# 预设学生名单
STUDENTS = [
   "熊梓睿",
    "周裕娟",
    "周渝芬",
    "钟佳莹",
    "涂廖芸",
    "李相怡",
    "齐玉洁",
    "石函宇",
    "刘欣",
    "陈智榕",
    "田书禾",
    "陈至岩",
    "杨中正",
    "吴昊",
    "浦俊书",
    "王雪坭",
    "邓森元",
    "李开湘",
    "薛馨阳"
]

def load_data():
    """加载签到数据"""
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {'checkedInStudents': [], 'records': []}
    except Exception as e:
        print(f"加载数据失败: {e}")
        return {'checkedInStudents': [], 'records': []}

def save_data(data):
    """保存签到数据"""
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"保存数据失败: {e}")
        return False

def load_ip_records():
    """加载IP记录"""
    try:
        if os.path.exists(IP_RECORDS_FILE):
            with open(IP_RECORDS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    except Exception as e:
        print(f"加载IP记录失败: {e}")
        return {}

def save_ip_records(records):
    """保存IP记录"""
    try:
        with open(IP_RECORDS_FILE, 'w', encoding='utf-8') as f:
            json.dump(records, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"保存IP记录失败: {e}")
        return False

def reset_all_data():
    """重置所有数据（签到记录和IP记录）"""
    try:
        # 重置签到数据
        empty_data = {'checkedInStudents': [], 'records': []}
        if save_data(empty_data):
            print("✅ 签到数据已重置")
        else:
            print("❌ 签到数据重置失败")
            
        # 重置IP记录
        empty_ip_records = {}
        if save_ip_records(empty_ip_records):
            print("✅ IP记录已重置")
        else:
            print("❌ IP记录重置失败")
            
        return True
    except Exception as e:
        print(f"重置数据失败: {e}")
        return False

# 系统启动时重置所有数据
print("🔄 系统启动，正在重置所有数据...")
reset_all_data()

@app.route('/')
def index():
    """提供主页面"""
    return send_from_directory('.', 'index.html')

@app.route('/guide')
def guide():
    """提供使用指南页面"""
    return send_from_directory('.', 'guide.html')

@app.route('/api/students', methods=['GET'])
def get_students():
    """获取学生名单"""
    return jsonify(STUDENTS)

@app.route('/api/checkin', methods=['POST'])
def checkin():
    """处理签到请求"""
    try:
        data = request.get_json()
        name = data.get('name', '').strip()
        
        if not name:
            return jsonify({'success': False, 'message': '请输入姓名'})
        
        if name not in STUDENTS:
            return jsonify({'success': False, 'message': '姓名不在学生名单中'})
        
        # 获取客户端IP
        client_ip = request.remote_addr
        user_agent = request.headers.get('User-Agent', '')
        
        # 加载当前数据
        checkin_data = load_data()
        ip_records = load_ip_records()
        
        # 检查是否已经签到
        if name in checkin_data['checkedInStudents']:
            return jsonify({'success': False, 'message': '该学生已经签到'})
        
        # 检查IP是否已经使用
        if client_ip in ip_records:
            # 获取已使用该IP的学生姓名
            original_student = ip_records[client_ip]['name']
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # 记录IP冲突事件
            if 'ip_conflict_events' not in checkin_data:
                checkin_data['ip_conflict_events'] = []
            
            conflict_event = {
                'timestamp': current_time,
                'originalName': original_student,
                'currentName': name,
                'ip': client_ip
            }
            checkin_data['ip_conflict_events'].append(conflict_event)
            save_data(checkin_data)  # 保存冲突事件
            
            return jsonify({
                'success': False, 
                'message': f'该IP地址已被 {original_student} 使用，无法代签！',
                'type': 'ip_conflict',
                'originalName': original_student,
                'currentName': name
            })
        
        # 添加签到记录
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        checkin_data['checkedInStudents'].append(name)
        checkin_data['records'].append({
            'name': name,
            'ip': client_ip,
            'time': current_time,
            'userAgent': user_agent
        })
        
        # 记录IP
        ip_records[client_ip] = {
            'name': name,
            'time': current_time,
            'userAgent': user_agent
        }
        
        # 保存数据
        if save_data(checkin_data) and save_ip_records(ip_records):
            return jsonify({
                'success': True, 
                'message': f'{name} 签到成功！',
                'checkedInStudents': checkin_data['checkedInStudents']
            })
        else:
            return jsonify({'success': False, 'message': '数据保存失败'})
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'签到失败: {e}'})

@app.route('/api/checkin-status', methods=['GET'])
def get_checkin_status():
    """获取签到状态"""
    try:
        checkin_data = load_data()
        
        # 检查是否有IP冲突事件需要广播
        ip_conflict_event = None
        if 'ip_conflict_events' in checkin_data and checkin_data['ip_conflict_events']:
            # 获取最新的IP冲突事件（5秒内的）
            current_time = datetime.now()
            recent_events = []
            for event in checkin_data['ip_conflict_events']:
                event_time = datetime.strptime(event['timestamp'], '%Y-%m-%d %H:%M:%S')
                if (current_time - event_time).total_seconds() < 5:  # 5秒内的冲突事件
                    recent_events.append(event)
            
            if recent_events:
                ip_conflict_event = recent_events[-1]  # 取最新的事件
        
        return jsonify({
            'checkedInStudents': checkin_data['checkedInStudents'],
            'totalStudents': len(STUDENTS),
            'checkedInCount': len(checkin_data['checkedInStudents']),
 'ipConflictEvent': ip_conflict_event
        })
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/records', methods=['GET'])
def get_records():
    """获取签到记录"""
    try:
        checkin_data = load_data()
        return jsonify(checkin_data['records'])
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/images/<path:filename>')
def serve_image(filename):
    """提供图片文件"""
    try:
        return send_from_directory('images', filename)
    except Exception as e:
        print(f"提供图片文件失败: {e}")
        return jsonify({'error': '图片文件不存在'}), 404

if __name__ == '__main__':
    print("🚀 启动打卡系统...")
    print(f"📋 预设学生名单: {len(STUDENTS)}人")
    print("💾 数据文件已加载")
    app.run(host='0.0.0.0', port=5000, debug=True)