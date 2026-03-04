from flask import Flask, render_template, request, redirect, url_for, jsonify
import sqlite3

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('queue.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/join', methods=['POST'])
def join():
    name = request.form['name']
    queue_code = request.form['queue_code']
    priority_request = request.form['priority_request']

    conn = get_db_connection()


    queue = conn.execute(
        'SELECT * FROM queues WHERE queue_code = ?',
        (queue_code,)
    ).fetchone()
    if queue is None:
        conn.close()
        return "Invalid Queue Code"



    existing = conn.execute(
        '''
        SELECT * FROM members
        WHERE name = ? AND queue_code = ? AND status = 'waiting'
        ''',
        (name, queue_code)
    ).fetchone()

    if existing:
        conn.close()
        return render_template(
            "index.html",
            error=f"{name} is already in the queue!"
        )


    cursor = conn.cursor()
    cursor.execute(
        '''
        INSERT INTO members (name, queue_code, priority_request, priority_status)
        VALUES (?, ?, ?, ?)
        ''',
        (name, queue_code, priority_request,
         'pending' if priority_request else 'none')
    )
    conn.commit()

    member_id = cursor.lastrowid
    member = conn.execute(
        'SELECT * FROM members WHERE id = ?',
        (member_id,)
    ).fetchone()


    position = conn.execute(
        '''
        SELECT COUNT(*) FROM members
        WHERE queue_code = ?
        AND status = 'waiting'
        AND (
            priority_level > ?
            OR (priority_level = ? AND joined_at < ?)
        )
        ''',
        (queue_code, member['priority_level'], member['priority_level'], member['joined_at'])
    ).fetchone()[0] + 1

    queue_name = queue['queue_name']
    conn.close()

    return render_template(
        "waiting.html",
        name=member['name'],
        member_id=member['id'],
        queue_name=queue_name,
        queue_code=queue_code,
        position=position,
        queue=[]
    )

@app.route('/waiting/<int:member_id>')
def waiting(member_id):
    conn = get_db_connection()
    member = conn.execute('SELECT * FROM members WHERE id = ?', (member_id,)).fetchone()
    if not member or member['status'] != 'waiting':
        conn.close()
        return "Member not in queue"

    queue_list = conn.execute(
        '''
        SELECT id, name, priority_status FROM members
        WHERE queue_code = ? AND status = 'waiting'
        ORDER BY priority_level DESC, joined_at ASC
        ''',
        (member['queue_code'],)
    ).fetchall()

    position = conn.execute(
        '''
        SELECT COUNT(*) FROM members
        WHERE queue_code = ?
        AND status = 'waiting'
        AND (
            priority_level > ?
            OR (priority_level = ? AND joined_at < ?)
        )
        ''',
        (member['queue_code'], member['priority_level'], member['priority_level'], member['joined_at'])
    ).fetchone()[0] + 1

    conn.close()

    return render_template(
        'waiting.html',
        name=member['name'],
        queue_code=member['queue_code'],
        queue_name=member['queue_code'],
        member_id=member['id'],
        position=position,
        queue=queue_list
    )


@app.route('/queue-status/<int:member_id>')
def queue_status(member_id):
    conn = get_db_connection()
    member = conn.execute('SELECT * FROM members WHERE id = ?', (member_id,)).fetchone()

    if not member or member['status'] != 'waiting':
        conn.close()
        return jsonify({'position': 0, 'queue': []})

    queue_list = conn.execute(
        '''
        SELECT id, name, priority_status FROM members
        WHERE queue_code = ? AND status = 'waiting'
        ORDER BY priority_level DESC, joined_at ASC
        ''',
        (member['queue_code'],)
    ).fetchall()

    position = conn.execute(
        '''
        SELECT COUNT(*) FROM members
        WHERE queue_code = ?
        AND status = 'waiting'
        AND (
            priority_level > ?
            OR (priority_level = ? AND joined_at < ?)
        )
        ''',
        (member['queue_code'], member['priority_level'], member['priority_level'], member['joined_at'])
    ).fetchone()[0] + 1

    conn.close()

    return jsonify({
        'position': position,
        'queue': [
            {'id': m['id'], 'name': m['name'], 'priority_status': m['priority_status']}
            for m in queue_list
        ]
    })


@app.route('/admin/queue/<queue_code>')
def admin_queue(queue_code):
    conn = get_db_connection()

    queue = conn.execute(
        "SELECT queue_name FROM queues WHERE queue_code = ?",
        (queue_code,)
    ).fetchone()

    members = conn.execute(
        "SELECT * FROM members WHERE queue_code = ? AND status = 'waiting'",
        (queue_code,)
    ).fetchall()

    conn.close()

    return render_template(
        "admin_queue.html",
        members=members,
        queue_code=queue_code,
        queue_name=queue["queue_name"] if queue else "Unknown Queue"
    )


@app.route('/admin/queue/<queue_code>/priority/<int:member_id>/<action>', methods=['POST'])
def admin_priority(queue_code, member_id, action):
    conn = get_db_connection()
    if action == 'approve':
        conn.execute('UPDATE members SET priority_status="approved", priority_level=1 WHERE id = ?', (member_id,))
    elif action == 'reject':
        conn.execute('UPDATE members SET priority_status="rejected", priority_level=0 WHERE id = ?', (member_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin_queue', queue_code=queue_code))


@app.route('/admin/queue/<queue_code>/advance/<int:member_id>', methods=['POST'])
def admin_advance(queue_code, member_id):
    conn = get_db_connection()
    conn.execute('UPDATE members SET status="served" WHERE id = ?', (member_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin_queue', queue_code=queue_code))


@app.route('/admin/queue/<queue_code>/remove/<int:member_id>', methods=['POST'])
def admin_remove(queue_code, member_id):
    conn = get_db_connection()
    conn.execute('UPDATE members SET status="removed" WHERE id = ?', (member_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin_queue', queue_code=queue_code))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)