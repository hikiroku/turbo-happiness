from flask import Flask, request, jsonify, render_template
from datetime import datetime
import os
import sqlite3
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# データベースの設定
def get_db_path():
    if 'VERCEL' in os.environ:
        return '/tmp/database.db'
    return 'database.db'

def get_db():
    db = sqlite3.connect(get_db_path())
    db.row_factory = sqlite3.Row
    return db

def init_db():
    db = get_db()
    db.execute('''
        CREATE TABLE IF NOT EXISTS todos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            completed BOOLEAN NOT NULL DEFAULT 0,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            ai_suggestion TEXT
        )
    ''')
    db.commit()
    db.close()

# OpenAI clientの設定
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

def get_ai_suggestion(todo_title):
    try:
        response = client.chat.completions.create(
            model="mistralai/mistral-7b-instruct",
            messages=[
                {
                    "role": "system",
                    "content": "あなたはTODOの解決をサポートする優秀なアシスタントです。ユーザーのタスクに対して、具体的で実践的なアドバイスを提供してください。"
                },
                {
                    "role": "user",
                    "content": f"「{todo_title}」というTODOがあります。このタスクを効率的に達成するためのアドバイスを3点、以下の形式で教えてください：\n\n1. [準備段階でのアドバイス]\n2. [実行段階でのアドバイス]\n3. [クオリティを高めるためのアドバイス]"
                }
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"AI提案の生成中にエラーが発生しました: {e}")
        return None

# アプリケーション起動時にデータベースを初期化
init_db()

# ルートページの表示
@app.route('/')
def index():
    return render_template('index.html')

# TODOの取得
@app.route('/api/todos', methods=['GET'])
def get_todos():
    db = get_db()
    todos = db.execute('SELECT * FROM todos ORDER BY created_at DESC').fetchall()
    db.close()
    return jsonify([{
        'id': todo['id'],
        'title': todo['title'],
        'completed': bool(todo['completed']),
        'created_at': todo['created_at'],
        'ai_suggestion': todo['ai_suggestion']
    } for todo in todos])

# TODOの追加
@app.route('/api/todos', methods=['POST'])
def add_todo():
    title = request.json.get('title')
    if not title:
        return jsonify({'error': 'Title is required'}), 400
    
    ai_suggestion = get_ai_suggestion(title)
    
    db = get_db()
    cursor = db.execute(
        'INSERT INTO todos (title, ai_suggestion) VALUES (?, ?)',
        (title, ai_suggestion)
    )
    todo_id = cursor.lastrowid
    db.commit()
    
    todo = db.execute('SELECT * FROM todos WHERE id = ?', (todo_id,)).fetchone()
    db.close()
    
    return jsonify({
        'id': todo['id'],
        'title': todo['title'],
        'completed': bool(todo['completed']),
        'created_at': todo['created_at'],
        'ai_suggestion': todo['ai_suggestion']
    }), 201

# TODOの更新（完了状態の切り替え）
@app.route('/api/todos/<int:todo_id>', methods=['PUT'])
def update_todo(todo_id):
    completed = request.json.get('completed', False)
    
    db = get_db()
    db.execute(
        'UPDATE todos SET completed = ? WHERE id = ?',
        (completed, todo_id)
    )
    db.commit()
    
    todo = db.execute('SELECT * FROM todos WHERE id = ?', (todo_id,)).fetchone()
    if todo is None:
        db.close()
        return jsonify({'error': 'Todo not found'}), 404
        
    result = {
        'id': todo['id'],
        'title': todo['title'],
        'completed': bool(todo['completed']),
        'created_at': todo['created_at'],
        'ai_suggestion': todo['ai_suggestion']
    }
    db.close()
    return jsonify(result)

# TODOの削除
@app.route('/api/todos/<int:todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    db = get_db()
    db.execute('DELETE FROM todos WHERE id = ?', (todo_id,))
    db.commit()
    db.close()
    return '', 204

if __name__ == '__main__':
    app.run(debug=True)
