document.addEventListener('DOMContentLoaded', () => {
    // DOM要素の取得
    const todoInput = document.getElementById('todo-input');
    const addTodoButton = document.getElementById('add-todo');
    const todoList = document.getElementById('todo-list');
    const filterButtons = document.querySelectorAll('.filter-btn');
    const todoTemplate = document.getElementById('todo-item-template');

    let currentFilter = 'all';
    let todos = [];

    // TODOの取得
    const fetchTodos = async () => {
        try {
            const response = await fetch('/api/todos');
            todos = await response.json();
            renderTodos();
        } catch (error) {
            console.error('TODOの取得に失敗しました:', error);
        }
    };

    // TODOの追加
    const addTodo = async () => {
        const title = todoInput.value.trim();
        if (!title) return;

        try {
            const response = await fetch('/api/todos', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ title }),
            });

            const newTodo = await response.json();
            todos.unshift(newTodo);
            renderTodos();
            todoInput.value = '';
        } catch (error) {
            console.error('TODOの追加に失敗しました:', error);
        }
    };

    // TODOの状態更新
    const updateTodoStatus = async (todoId, completed) => {
        try {
            const response = await fetch(`/api/todos/${todoId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ completed }),
            });

            const updatedTodo = await response.json();
            todos = todos.map(todo => 
                todo.id === updatedTodo.id ? updatedTodo : todo
            );
            renderTodos();
        } catch (error) {
            console.error('TODOの更新に失敗しました:', error);
        }
    };

    // TODOの削除
    const deleteTodo = async (todoId) => {
        try {
            await fetch(`/api/todos/${todoId}`, {
                method: 'DELETE',
            });

            todos = todos.filter(todo => todo.id !== todoId);
            renderTodos();
        } catch (error) {
            console.error('TODOの削除に失敗しました:', error);
        }
    };

    // TODOアイテムの作成
    const createTodoElement = (todo) => {
        const template = todoTemplate.content.cloneNode(true);
        const todoItem = template.querySelector('.todo-item');
        const checkbox = template.querySelector('.todo-checkbox');
        const todoText = template.querySelector('.todo-text');
        const deleteButton = template.querySelector('.delete-btn');

        todoItem.dataset.id = todo.id;
        if (todo.completed) {
            todoItem.classList.add('completed');
        }
        checkbox.checked = todo.completed;
        todoText.textContent = todo.title;

        // イベントリスナーの設定
        checkbox.addEventListener('change', () => {
            updateTodoStatus(todo.id, checkbox.checked);
        });

        deleteButton.addEventListener('click', () => {
            deleteTodo(todo.id);
        });

        return todoItem;
    };

    // TODOリストの表示
    const renderTodos = () => {
        todoList.innerHTML = '';
        const filteredTodos = todos.filter(todo => {
            if (currentFilter === 'active') return !todo.completed;
            if (currentFilter === 'completed') return todo.completed;
            return true;
        });

        filteredTodos.forEach(todo => {
            todoList.appendChild(createTodoElement(todo));
        });
    };

    // フィルターの切り替え
    filterButtons.forEach(button => {
        button.addEventListener('click', () => {
            filterButtons.forEach(btn => btn.classList.remove('active'));
            button.classList.add('active');
            currentFilter = button.dataset.filter;
            renderTodos();
        });
    });

    // イベントリスナーの設定
    addTodoButton.addEventListener('click', addTodo);
    todoInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            addTodo();
        }
    });

    // 初期表示
    fetchTodos();
});
