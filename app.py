from flask import Flask, request, jsonify, render_template
import sqlite3
from datetime import datetime

app = Flask(__name__)

# データベースの初期化
def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS todos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            completed BOOLEAN NOT NULL DEFAULT 0,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
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
    todos = [{'id': row[0], 'title': row[1], 'completed': bool(row[2]), 'created_at': row[3]} 
             for row in c.fetchall()]
    conn.close()
    return jsonify(todos)

# TODOの追加
@app.route('/api/todos', methods=['POST'])
def add_todo():
    title = request.json.get('title')
    if not title:
        return jsonify({'error': 'Title is required'}), 400
    
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('INSERT INTO todos (title) VALUES (?)', (title,))
    todo_id = c.lastrowid
    conn.commit()
    
    c.execute('SELECT * FROM todos WHERE id = ?', (todo_id,))
    todo = c.fetchone()
    conn.close()
    
    return jsonify({
        'id': todo[0],
        'title': todo[1],
        'completed': bool(todo[2]),
        'created_at': todo[3]
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
        'created_at': todo[3]
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
