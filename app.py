from flask import Flask, request, jsonify, render_template
import sqlite3
from datetime import datetime
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

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
                    "content": "あなたはTODOの解決をサポートする優秀なアシスタントです。"
                },
                {
                    "role": "user",
                    "content": f"「{todo_title}」というTODOがあります。これを効率的に達成するためのアドバイスを3点、箇条書きで簡潔に教えてください。"
                }
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"AI提案の生成中にエラーが発生しました: {e}")
        return None

# データベースの初期化
def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS todos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            completed BOOLEAN NOT NULL DEFAULT 0,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            ai_suggestion TEXT
        )
    ''')
    conn.commit()
    conn.close()

# アプリケーション起動時にデータベースを初期化
init_db()

# ルートページの表示
@app.route('/')
def index():
    return render_template('index.html')

# TODOの取得
@app.route('/api/todos', methods=['GET'])
def get_todos():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('SELECT * FROM todos ORDER BY created_at DESC')
    todos = [{'id': row[0], 'title': row[1], 'completed': bool(row[2]), 'created_at': row[3], 'ai_suggestion': row[4]} 
             for row in c.fetchall()]
    conn.close()
    return jsonify(todos)

# TODOの追加
@app.route('/api/todos', methods=['POST'])
def add_todo():
    title = request.json.get('title')
    if not title:
        return jsonify({'error': 'Title is required'}), 400
    
    # AI提案を生成
    ai_suggestion = get_ai_suggestion(title)
    
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('INSERT INTO todos (title, ai_suggestion) VALUES (?, ?)', (title, ai_suggestion))
    todo_id = c.lastrowid
    conn.commit()
    
    c.execute('SELECT * FROM todos WHERE id = ?', (todo_id,))
    todo = c.fetchone()
    conn.close()
    
    return jsonify({
        'id': todo[0],
        'title': todo[1],
        'completed': bool(todo[2]),
        'created_at': todo[3],
        'ai_suggestion': todo[4]
    }), 201

# TODOの更新（完了状態の切り替え）
@app.route('/api/todos/<int:todo_id>', methods=['PUT'])
def update_todo(todo_id):
    completed = request.json.get('completed', False)
    
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('UPDATE todos SET completed = ? WHERE id = ?', (completed, todo_id))
    conn.commit()
    
    c.execute('SELECT * FROM todos WHERE id = ?', (todo_id,))
    todo = c.fetchone()
    conn.close()
    
    if todo is None:
        return jsonify({'error': 'Todo not found'}), 404
    
    return jsonify({
        'id': todo[0],
        'title': todo[1],
        'completed': bool(todo[2]),
        'created_at': todo[3],
        'ai_suggestion': todo[4]
    })

# TODOの削除
@app.route('/api/todos/<int:todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('DELETE FROM todos WHERE id = ?', (todo_id,))
    conn.commit()
    conn.close()
    return '', 204

if __name__ == '__main__':
    app.run(debug=True)
