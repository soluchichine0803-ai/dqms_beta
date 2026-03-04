import sqlite3

# Connect to your database
conn = sqlite3.connect('queue.db')
cursor = conn.cursor()

# Insert a test queue
cursor.execute('''
    INSERT INTO queues (queue_code, queue_name)
    VALUES (?, ?)
''', ('TEST123', 'Main Test Queue'))

# Commit and close
conn.commit()
conn.close()

print("Success")