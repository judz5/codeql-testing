from flask import Flask, request, render_template_string
import html, sqlite3

app = Flask (__name__)

db = 'database.db'

def init_db():
    with sqlite3.connect(db) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL
            )
        ''')

        # this just sets up some fake database for PoC purposes
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                password TEXT NOT NULL
            )
        ''')
        # fake users info
        cursor.execute("INSERT OR IGNORE INTO users (username, password) VALUES ('admin', 'admin123')")
        cursor.execute("INSERT OR IGNORE INTO users (username, password) VALUES ('user1', 'password123')")
        cursor.execute("INSERT OR IGNORE INTO users (username, password) VALUES ('guest', 'guestpass')")

        conn.commit()

def get_tasks(search):
    with sqlite3.connect(db) as conn:
        cursor = conn.cursor()
        # now using paramaterized queries... very very nice. and secure.
        query = f"SELECT content FROM tasks WHERE content LIKE ?"
        cursor.execute(query, ('%' + search + '%',))
        return [row[0] for row in cursor.fetchall()]

def add_task_db(task):
    with sqlite3.connect(db) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO tasks (content) VALUES (?)", (task,))
        conn.commit()

@app.route('/')
def index():
    search = request.args.get('search', '')

    tasks = get_tasks(search=search)

    return render_template_string("""
        <h1>SQL injection todo</h1>
        <ul>
            {% for task in tasks %}
                <li>{{ task|safe }}</li>
            {% endfor %}
        </ul>
        <form action="/task" method="POST">
            New Task: <input type="text" name="todo" required><br>
            <input type="submit" value="Add Task">
        </form>

        <h2>Search Tasks</h2>
        <form method="GET" action="/">
            Search: <input type="text" name="search" value="{{ search_query }}">
            <input type="submit" value="Search">
        </form>

        {% if search_query %}
            <h3>Search Results for: {{ search_query|safe }}</h3>
            <ul>
                {% for task in filtered_tasks %}
                    <li>{{ task|safe }}</li>
                {% endfor %}
            </ul>
        {% endif %}
    """, tasks=tasks, search_query=search)

@app.route('/task', methods=['POST'])
def add_task():
    task = request.form.get('todo')
    add_task_db(task)
    return index()

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=80, debug=True, threaded=True)
