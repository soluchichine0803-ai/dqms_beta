
A lightweight web-based queue management system built with **Flask** and **SQLite**.  
It allows users to join queues, request priority access, and enables admins to manage queue members in real time.

---

## Features

### User Features
- Join a queue using a queue code
- Optional priority request when joining
- View live queue position
- Real-time queue updates
- Automatic notification when:
  - Served
  - Removed from queue

### Admin Features
- View all waiting members in a queue
- Approve or reject priority requests
- Serve (advance) members
- Remove members from the queue

---

## Tech Stack

- **Backend:** Python (Flask)
- **Database:** SQLite
- **Frontend:** HTML, CSS, JavaScript
- **Templating Engine:** Jinja2

---

## Project Structure

.
├── app.py  
├── queue.db  
├── templates/  
│   ├── index.html  
│   ├── waiting.html  
│   └── admin_queue.html  
└── static/

---

## Installation & Setup

### 1️Clone the Repository

```bash
git clone https://github.com/yourusername/your-repo-name.git
cd your-repo-name
```

### 2️Create Virtual Environment (Recommended)

```bash
python -m venv venv
```

Activate the environment:

**macOS/Linux**
```bash
source venv/bin/activate
```

**Windows**
```bash
venv\Scripts\activate
```

### 3️Install Dependencies

```bash
pip install flask
```

### 4️Run the Application

```bash
python app.py
```

The application will run at:

http://localhost:5000

---

## Database Schema

### Queues Table
- queue_code
- queue_name

### Members Table
- id
- name
- queue_code
- priority_request
- priority_status
- priority_level
- status
- joined_at

---

## Queue Ordering Logic

Queue order is determined by:

1. priority_level (higher first)
2. joined_at (earlier first)

This ensures:
- Approved priority members are served first
- Regular members follow FIFO (First In, First Out) order

---

## API Endpoint

### Get Queue Status

GET /queue-status/<member_id>

### Example Response

```json
{
  "position": 2,
  "queue": [
    {
      "id": 1,
      "name": "John",
      "priority_status": "approved"
    }
  ]
}
```

---

## Future Improvements

- Admin authentication & role management
- Create/manage queues from the UI
- WebSocket-based real-time updates
- Docker containerization
- Cloud deployment (Render / Railway / AWS)

---

## License

This project is open-source and available under the MIT License.