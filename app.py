from flask import Flask, render_template_string, request, redirect, url_for, jsonify, session
from database_handler import DatabaseHandler
from food_algorithm import FoodAlgorithm
from exercise_algorithm import ExerciseAlgorithm
from chat_manager import ChatManager
import sys
import os

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'
app.config['JSON_AS_ASCII'] = False

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

food_path = os.path.join(BASE_DIR, "daily_food_nutrition_dataset.csv")
workout_path = os.path.join(BASE_DIR, "workouts_dataset.xlsx")

db_handler = DatabaseHandler()
food_algo = FoodAlgorithm(food_path)
exercise_algo = ExerciseAlgorithm(workout_path)
chat_manager = ChatManager(food_algo, exercise_algo, db_handler)

AUTH_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>AI Gym Assistant</title>
    <style>
        * {
            margin:0;
            padding:0;
            box-sizing:border-box;
            font-family:'Segoe UI';
        }
        body {
            background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);
            min-height:100vh;
            display:flex;
            justify-content:center;
            align-items:center;
        }
        .container {
            background:white;
            border-radius:20px;
            padding:40px;
            width:450px;
            box-shadow:0 20px 60px rgba(0,0,0,0.3);
        }
        .logo {
            text-align:center;
            margin-bottom:30px;
        }
        .logo h1 {
            color:#333;
        }
        .tabs {
            display:flex;
            margin-bottom:30px;
            background:#f0f0f0;
            border-radius:10px;
            padding:5px;
        }
        .tab {
            flex:1;
            padding:12px;
            text-align:center;
            cursor:pointer;
            border-radius:8px;
            border:none;
            background:transparent;
        }
        .tab.active {
            background:#667eea;
            color:white;
        }
        .form {
            display:none;
        }
        .form.active {
            display:block;
        }
        .input-group {
            margin-bottom:20px;
        }
        .input-group input {
            width:100%;
            padding:15px;
            border:2px solid #e0e0e0;
            border-radius:10px;
            outline:none;
        }
        .input-group input:focus {
            border-color:#667eea;
        }
        .submit-btn {
            width:100%;
            padding:16px;
            background:#667eea;
            border:none;
            border-radius:10px;
            color:white;
            font-weight:700;
            cursor:pointer;
        }
        .error-msg {
            background:#ff4757;
            color:white;
            padding:10px;
            border-radius:8px;
            margin-bottom:15px;
            text-align:center;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">
            <h1>🏋️ AI Gym Assistant</h1>
            <p>Your Personal AI Trainer</p>
        </div>
        <div class="tabs">
            <button class="tab active" onclick="showForm('login')">Sign In</button>
            <button class="tab" onclick="showForm('register')">Create Account</button>
        </div>
        
        {% if error %}
        <div class="error-msg">{{ error }}</div>
        {% endif %}
        
        <form class="form active" id="loginForm" method="POST" action="/login">
            <div class="input-group">
                <input type="text" name="username" placeholder="Username" required>
            </div>
            <div class="input-group">
                <input type="password" name="password" placeholder="Password" required>
            </div>
            <button type="submit" class="submit-btn">Sign In</button>
        </form>
        
        <form class="form" id="registerForm" method="POST" action="/register">
            <div class="input-group">
                <input type="text" name="full_name" placeholder="Full Name" required>
            </div>
            <div class="input-group">
                <input type="text" name="username" placeholder="Username" required>
            </div>
            <div class="input-group">
                <input type="email" name="email" placeholder="Email" required>
            </div>
            <div class="input-group">
                <input type="password" name="password" placeholder="Password" required>
            </div>
            <button type="submit" class="submit-btn">Create Account</button>
        </form>
    </div>
    
    <script>
        function showForm(formType) {
            document.querySelectorAll('.tab').forEach(tab => {
                tab.classList.remove('active');
            });
            event.target.classList.add('active');
            
            document.querySelectorAll('.form').forEach(form => {
                form.classList.remove('active');
            });
            document.getElementById(formType + 'Form').classList.add('active');
        }
    </script>
</body>
</html>
"""

CHAT_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>AI Gym Assistant - Chat</title>
    <style>
        * {
            margin:0;
            padding:0;
            box-sizing:border-box;
            font-family:'Segoe UI';
        }
        body {
            background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);
            min-height:100vh;
            display:flex;
            justify-content:center;
            align-items:center;
            padding:20px;
        }
        .chat-container {
            width:100%;
            max-width:900px;
            height:90vh;
            background:white;
            border-radius:20px;
            display:flex;
            flex-direction:column;
            overflow:hidden;
        }
        .chat-header {
            background:#667eea;
            padding:20px 25px;
            display:flex;
            align-items:center;
            gap:15px;
            color:white;
        }
        .bot-avatar {
            width:50px;
            height:50px;
            background:white;
            border-radius:50%;
            display:flex;
            align-items:center;
            justify-content:center;
            font-size:28px;
        }
        .header-info {
            flex:1;
        }
        .status {
            display:flex;
            align-items:center;
            gap:6px;
        }
        .status-dot {
            width:8px;
            height:8px;
            background:#4ade80;
            border-radius:50%;
            animation:pulse 2s infinite;
        }
        @keyframes pulse {
            0%,100%{opacity:1;}
            50%{opacity:0.5;}
        }
        .logout-btn {
            background:rgba(255,255,255,0.2);
            padding:8px 15px;
            border-radius:20px;
            color:white;
            text-decoration:none;
        }
        .chat-messages {
            flex:1;
            padding:25px;
            overflow-y:auto;
            background:#f8f9fa;
            display:flex;
            flex-direction:column;
            gap:15px;
        }
        .message {
            max-width:80%;
            padding:12px 18px;
            border-radius:18px;
            white-space:pre-wrap;
        }
        .user-message {
            align-self:flex-end;
            background:#667eea;
            color:white;
        }
        .bot-message {
            align-self:flex-start;
            background:white;
            color:#333;
            box-shadow:0 2px 10px rgba(0,0,0,0.1);
        }
        .welcome-message {
            text-align:center;
            color:#666;
            margin:auto;
        }
        .input-container {
            padding:20px 25px;
            background:white;
            border-top:1px solid #e0e0e0;
        }
        .input-box {
            display:flex;
            gap:12px;
        }
        .message-input {
            flex:1;
            padding:15px 20px;
            border:2px solid #e0e0e0;
            border-radius:25px;
            outline:none;
        }
        .message-input:focus {
            border-color:#667eea;
        }
        .send-btn {
            width:50px;
            height:50px;
            border-radius:50%;
            background:#667eea;
            border:none;
            color:white;
            font-size:20px;
            cursor:pointer;
        }
    </style>
</head>
<body>
    <div class="chat-container">
        <div class="chat-header">
            <div class="bot-avatar">🤖</div>
            <div class="header-info">
                <h2>AI Gym Assistant</h2>
                <div class="status">
                    <span class="status-dot"></span>
                    <span>Online</span>
                </div>
            </div>
            <a href="/logout" class="logout-btn">Logout</a>
        </div>
        
        <div class="chat-messages" id="chatMessages">
        </div>
        
        <div class="input-container">
            <div class="input-box">
                <input type="text" class="message-input" id="messageInput" 
                       placeholder="Type your message..." onkeypress="if(event.key=='Enter') sendMessage()">
                <button class="send-btn" onclick="sendMessage()">➤</button>
            </div>
        </div>
    </div>
    
    <script>
        let msgCount = 0;
        
        function addMessage(text, isUser) {
            let messagesDiv = document.getElementById('chatMessages');
            let messageDiv = document.createElement('div');
            messageDiv.className = isUser ? 'message user-message' : 'message bot-message';
            
            let formattedText = text.replace(/\\n/g, '<br>').replace(/\\*\\*(.*?)\\*\\*/g, '<strong>$1</strong>');
            messageDiv.innerHTML = formattedText;
            
            messagesDiv.appendChild(messageDiv);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
            msgCount++;
        }
        
        function sendMessage() {
            let input = document.getElementById('messageInput');
            let message = input.value.trim();
            
            if (message === '') return;
            
            addMessage(message, true);
            input.value = '';
            
            fetch('/send_message', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ message: message })
            })
            .then(response => response.json())
            .then(data => {
                addMessage(data.reply, false);
            })
            .catch(error => {
                addMessage('❌ Sorry, an error occurred. Please try again.', false);
            });
        }
        
        window.onload = function() {
            fetch('/first_message', {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.message) {
                    addMessage(data.message, false);
                }
            })
            .catch(error => {
                console.error('Error:', error);
            });
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    if 'username' in session:
        return redirect(url_for('chat'))
    return render_template_string(AUTH_PAGE, error=None)

@app.route('/chat')
def chat():
    if 'username' not in session:
        return redirect(url_for('home'))
    return render_template_string(CHAT_PAGE, username=session['username'])

@app.route('/first_message', methods=['GET'])
def first_message():
    if 'username' not in session:
        return jsonify({"message": "Please login first"})
    
    username = session['username']
    first_question = chat_manager.get_initial_question(username)
    return jsonify({"message": first_question})

@app.route('/register', methods=['POST'])
def register():
    full_name = request.form['full_name']
    username = request.form['username']
    email = request.form['email']
    password = request.form['password']
    
    if db_handler.create_user(full_name, username, email, password):
        session['username'] = username
        return redirect(url_for('chat'))
    
    return render_template_string(AUTH_PAGE, error="Username already exists")

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    
    user = db_handler.verify_user(username, password)
    if user:
        session['username'] = user['username']
        return redirect(url_for('chat'))
    
    return render_template_string(AUTH_PAGE, error="Invalid credentials")

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route('/send_message', methods=['POST'])
def send_message():
    if 'username' not in session:
        return jsonify({"reply": "Please login first"})
    
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({"reply": "No message received"})
        
        user_message = data['message']
        username = session['username']
        
        reply = chat_manager.get_reply(username, user_message)
        
        return jsonify({"reply": reply})
        
    except Exception as e:
        return jsonify({"reply": f"❌ Error: {str(e)}"})

if __name__ == '__main__':
    app.run(debug=True, port=5000)