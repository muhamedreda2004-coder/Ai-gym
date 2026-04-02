# 🏋️‍♂️ AI Gym Assistant

An intelligent web-based fitness and nutrition assistant powered by AI.
The system generates personalized **diet plans**, **workout routines**, and provides **real-time chat support** using a large language model.

---

# 🚀 Features

* 🔐 User Authentication (Login / Register)
* 🥗 Personalized Diet Plan (AI-based)
* 💪 Workout Plan Generator
* 🤖 AI Chat Assistant (Mistral 7B via Ollama)
* 🧠 Deep Learning Food Recommendation Model
* 🗄️ MySQL Database Integration

---

# 🧰 Requirements

Make sure you have the following installed:

* Python 3.9+
* MySQL Server
* Git
* Ollama (for AI chatbot)

---

# 📦 Python Libraries

Install all required libraries using:

```bash
pip install -r requirements.txt
```

Or install manually:

```bash
pip install flask pandas numpy scikit-learn tensorflow mysql-connector-python werkzeug openpyxl ollama
```

---

# 🤖 AI Model Setup (IMPORTANT)

This project uses **Mistral 7B** via Ollama.

### 1. Install Ollama

Download from: https://ollama.com

---

### 2. Pull the model

```bash
ollama pull mistral:7b-instruct-q4_0
```

---

### 3. Run Ollama

```bash
ollama run mistral:7b-instruct-q4_0
```

---

# 🗄️ Database Setup (MySQL)

### 1. Create Database

```sql
CREATE DATABASE gymai;
```

---

### 2. Import Tables

Run this file:

```bash
database.sql
```

Or manually:

```sql
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE,
    password VARCHAR(255),
    full_name VARCHAR(100),
    email VARCHAR(100),
    height VARCHAR(10),
    weight VARCHAR(10),
    age VARCHAR(5),
    gender VARCHAR(10),
    fitness_goal VARCHAR(100),
    training_days VARCHAR(50),
    activity_level VARCHAR(50),
    injuries TEXT,
    allergies TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

# ⚙️ Configuration

Create a `.env` file in the root directory:

```env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=yourpassword
DB_NAME=gymai
SECRET_KEY=yoursecretkey
```

---

# 📁 Project Structure

```
AI-Gym-Assistant/
│
├── app.py
├── database_handler.py
├── food_algorithm.py
├── exercise_algorithm.py
├── chat_manager.py
│
├── database.sql
├── requirements.txt
├── .env
│
├── datasets/
│   ├── daily_food_nutrition_dataset.csv
│   └── workouts_dataset.xlsx
│
└── README.md
```

---

# ▶️ How to Run the Project

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

---

### 2. Setup database (MySQL)

* Create database `gymai`
* Import `database.sql`

---

### 3. Run Ollama (VERY IMPORTANT)

```bash
ollama run mistral:7b-instruct-q4_0
```

---

### 4. Run the Flask app

```bash
python app.py
```

---

### 5. Open in browser

```
http://127.0.0.1:5000
```

---

# 📊 Datasets Used

### 🥗 Food Dataset

https://www.kaggle.com/datasets/adilshamim8/daily-food-and-nutrition-dataset

### 🏋️ Exercise Dataset

https://www.kaggle.com/datasets/peshimaammuzammil/the-ultimate-gym-exercises-dataset-for-all-levels

---

# 👨‍💻 Team

* Mohamed Reda (Leader)
* Ibrahim Mohamed Hosny
* Karim Adel Moamen
* Youssef Adel El-Essawy

---

# 💡 Future Improvements

* Deploy as a full production web app
* Add mobile app support
* Improve AI model performance
* Enhance UI/UX
