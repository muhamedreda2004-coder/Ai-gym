from datetime import datetime

try:
    import ollama
    OLLAMA_AVAILABLE = True
except Exception:
    ollama = None
    OLLAMA_AVAILABLE = False

class ChatManager:
    def __init__(self, food_algo, exercise_algo, db_handler):
        self.food = food_algo
        self.exercise = exercise_algo
        self.db = db_handler
        self.user_sessions = {}

        self.profile_questions = [
            {"key": "height", "question": "🏋️‍♂️ **Welcome to your AI Personal Trainer!** 🤖\n\nI'm here to help you achieve your fitness goals. Let me get to know you first.\n\n📏 **What is your height?** (in cm, e.g., 175)", "validate": lambda x: x.isdigit() and 100 <= int(x) <= 250, "error": "❌ Height must be between 100-250 cm.", "process": lambda x: int(x)},
            {"key": "weight", "question": "⚖️ **Great! What is your weight?** (in kg, e.g., 70)", "validate": lambda x: x.isdigit() and 30 <= int(x) <= 200, "error": "❌ Weight must be between 30-200 kg.", "process": lambda x: int(x)},
            {"key": "age", "question": "📅 **How old are you?**", "validate": lambda x: x.isdigit() and 13 <= int(x) <= 100, "error": "❌ Age must be between 13-100 years.", "process": lambda x: int(x)},
            {"key": "gender", "question": "👤 **What is your gender?** (male/female)", "validate": lambda x: x.lower() in ['male', 'female', 'm', 'f'], "error": "❌ Please enter 'male' or 'female'", "process": lambda x: 'male' if x.lower() in ['male', 'm'] else 'female'},
            {"key": "goal", "question": "🎯 **What is your main fitness goal?**\n• lose weight\n• gain muscle\n• stay fit", "validate": lambda x: any(word in x.lower() for word in ['lose', 'weight', 'gain', 'muscle', 'stay', 'fit']), "error": "❌ Please choose: lose weight, gain muscle, or stay fit", "process": lambda x: self._extract_goal(x)},
            {"key": "training_days", "question": "📆 **How many days per week can you train?** (1-7 days)", "validate": lambda x: x.isdigit() and 1 <= int(x) <= 7, "error": "❌ Please enter a number between 1-7", "process": lambda x: int(x)},
            {"key": "activity_level", "question": "💼 **How would you describe your daily activity?**\n• sedentary\n• light\n• moderate\n• active\n• very active", "validate": lambda x: x.lower() in ['sedentary', 'light', 'moderate', 'active', 'very active'], "error": "❌ Please choose: sedentary, light, moderate, active, or very active", "process": lambda x: x.lower()}
        ]

        self.extra_questions = [
            {"key": "injuries", "question": "⚠️ **Do you have any injuries or health conditions?** (If none, type 'none')", "validate": lambda x: True, "process": lambda x: x if x.lower() != 'none' else ''},
            {"key": "allergies", "question": "🍽️ **Do you have any food allergies?** (If none, type 'none')", "validate": lambda x: True, "process": lambda x: x if x.lower() != 'none' else ''}
        ]

    def _extract_goal(self, text):
        text = text.lower()
        if any(word in text for word in ['lose', 'weight', 'fat']):
            return 'lose weight'
        elif any(word in text for word in ['gain', 'muscle', 'build']):
            return 'gain muscle'
        return 'stay fit'

    def get_initial_question(self, username):
        if username not in self.user_sessions:
            self.user_sessions[username] = {
                'stage': 'profile',
                'question_index': 1,
                'profile_data': {},
                'extra_index': 0
            }
        return self.profile_questions[0]['question']

    def get_reply(self, username, message):
        if username not in self.user_sessions:
            self.user_sessions[username] = {
                'stage': 'profile',
                'question_index': 1,
                'profile_data': {},
                'extra_index': 0
            }

        session = self.user_sessions[username]

        if session['stage'] == 'profile':
            return self._handle_profile_stage(username, message, session)
        elif session['stage'] == 'awaiting_extra_questions':
            return self._handle_extra_questions_stage(username, message, session)
        elif session['stage'] == 'awaiting_diet_plan':
            return self._handle_diet_plan_request(username, message, session)
        elif session['stage'] == 'awaiting_diet_plan_review':
            return self._handle_diet_plan_review(username, message, session)
        elif session['stage'] == 'awaiting_workout_plan':
            return self._handle_workout_plan_request(username, message, session)
        else:
            return self._handle_ai_chat(username, message, session)

    def _handle_profile_stage(self, username, message, session):
        q_index = session['question_index']

        current_q = self.profile_questions[q_index - 1]

        if not current_q['validate'](message):
            return f"{current_q['error']}\n\n{current_q['question']}"

        session['profile_data'][current_q['key']] = current_q['process'](message)

        if q_index >= len(self.profile_questions):
            self.db.update_user_data(username, session['profile_data'])
            session['stage'] = 'awaiting_extra_questions'
            session['extra_index'] = 0
            return self.extra_questions[0]['question']

        next_q = self.profile_questions[q_index]
        session['question_index'] += 1
        return next_q['question']

    def _handle_extra_questions_stage(self, username, message, session):
        idx = session['extra_index']
        current_q = self.extra_questions[idx]

        answer = current_q['process'](message)
        session['profile_data'][current_q['key']] = answer

        if idx + 1 >= len(self.extra_questions):
            extra_data = {q['key']: session['profile_data'][q['key']] for q in self.extra_questions}
            self.db.update_extra_data(username, extra_data)
            session['stage'] = 'awaiting_diet_plan'
            return "✅ **Great!** Your profile is complete.\n\nWould you like me to create a personalized **diet plan** for you? (yes/no)"

        session['extra_index'] += 1
        return self.extra_questions[idx + 1]['question']


   

    def _handle_diet_plan_request(self, username, message, session):
        if message.lower() in ['yes', 'y', 'sure', 'ok', 'please', 'yeah', 'yep']:
            profile = session['profile_data'].copy()
            meal_plan = self.food.generate_meal_plan(profile)
            needs = meal_plan['daily_needs']

            # حفظ الأطعمة المستخدمة
            session['used_foods'] = []
            for meal in meal_plan['meals'].values():
                for food in meal['foods']:
                    session['used_foods'].append(food['name'])
            session['current_meal_plan'] = meal_plan

            response = "📋 **Your Personalized Nutrition Plan**\n\n"
            response += "**📊 Daily Targets**\n"
            response += f"🔥 Calories: `{int(needs['calories'])} kcal`\n"
            response += f"🥩 Protein: `{int(needs['protein'])} g`\n"
            response += f"🍚 Carbs:   `{int(needs['carbs'])} g`\n"
            response += f"🥑 Fat:     `{int(needs['fat'])} g`\n\n"
            response += "─" * 40 + "\n\n"

            for meal_key, meal in meal_plan['meals'].items():
                response += f"**{meal['name']}**  `{int(meal['calories'])} kcal`\n"
                for food in meal['foods']:
                    response += f"   • {food['name']}  →  {food['serving']}\n"
                    if meal_key in ['breakfast', 'lunch', 'dinner']:
                        response += f"     *{int(food['protein'])}g protein · {int(food['carbs'])}g carbs · {int(food['fat'])}g fat*\n"
                response += "\n"

            response += "💧 **Water:** Drink 2–3 liters daily.\n"
            response += "\n**Do you like this plan?**\n"
            response += "• Type **`yes`** to accept and get a workout plan.\n"
            response += "• Type **`change`** to generate a new plan (different foods).\n"
            response += "• Type **`no`** if you don't want a workout plan later.\n"

            session['stage'] = 'awaiting_diet_plan_review'
            return response

        elif message.lower() in ['no', 'n', 'not now', 'later']:
            session['stage'] = 'awaiting_workout_plan'
            return "No problem! Would you like a **workout plan** instead? (yes/no)"

        else:
            return "Please answer with **yes** or **no**"

    def _handle_diet_plan_review(self, username, message, session):
        if message.lower() in ['yes', 'y', 'sure', 'ok', 'accept']:
            session['stage'] = 'awaiting_workout_plan'
            return "Great! Would you like a **workout plan** as well? (yes/no)"

        elif message.lower() in ['change', 'new', 'different']:
            profile = session['profile_data'].copy()
            used_foods = session.get('used_foods', [])
            meal_plan = self.food.generate_meal_plan(profile, exclude_foods=used_foods)
            needs = meal_plan['daily_needs']

            # تحديث قائمة الأطعمة المستخدمة
            new_foods = []
            for meal in meal_plan['meals'].values():
                for food in meal['foods']:
                    new_foods.append(food['name'])
            session['used_foods'].extend(new_foods)
            session['current_meal_plan'] = meal_plan

            response = "📋 **New Nutrition Plan**\n\n"
            response += "**📊 Daily Targets**\n"
            response += f"🔥 Calories: `{int(needs['calories'])} kcal`\n"
            response += f"🥩 Protein: `{int(needs['protein'])} g`\n"
            response += f"🍚 Carbs:   `{int(needs['carbs'])} g`\n"
            response += f"🥑 Fat:     `{int(needs['fat'])} g`\n\n"
            response += "─" * 40 + "\n\n"

            for meal_key, meal in meal_plan['meals'].items():
                response += f"**{meal['name']}**  `{int(meal['calories'])} kcal`\n"
                for food in meal['foods']:
                    response += f"   • {food['name']}  →  {food['serving']}\n"
                    if meal_key in ['breakfast', 'lunch', 'dinner']:
                        response += f"     *{int(food['protein'])}g protein · {int(food['carbs'])}g carbs · {int(food['fat'])}g fat*\n"
                response += "\n"

            response += "💧 **Water:** Drink 2–3 liters daily.\n"
            response += "\n**Do you like this new plan?**\n"
            response += "• Type **`yes`** to accept and get a workout plan.\n"
            response += "• Type **`change`** to get another plan.\n"

            return response

        elif message.lower() in ['no', 'n', 'skip']:
            session['stage'] = 'ai_chat'
            return self._get_ai_welcome_message()

        else:
            return "Please answer with **yes** (accept plan), **change** (new plan), or **no** (skip workout plan)."

    # ... (باقي الدوال كما هي)

    def _handle_workout_plan_request(self, username, message, session):
        if message.lower() in ['yes', 'y', 'sure', 'ok', 'please', 'yeah', 'yep']:
            profile = session['profile_data']
            workout_plan = self.exercise.generate_workout_plan(profile)
            response = workout_plan + "\n\n" + self._get_ai_welcome_message()
            session['stage'] = 'ai_chat'
            return response

        elif message.lower() in ['no', 'n', 'not now', 'later']:
            session['stage'] = 'ai_chat'
            return self._get_ai_welcome_message()

        else:
            return "Please answer with **yes** or **no**"

    def _get_ai_welcome_message(self):
        return """🎉 **You're all set!** 🎉

🤖 **Now you can ask me ANYTHING about:**
• 💪 Exercise techniques and workout plans
• 🥗 Nutrition and meal ideas
• 🏋️‍♂️ Fitness tips and advice
• 📈 Progress tracking
• 🔥 Motivation and mindset

💬 **Just type your question naturally!**

**Ask me anything!** 🚀"""

    def _handle_ai_chat(self, username, message, session):
        try:
            profile = session.get('profile_data', {})
            if not OLLAMA_AVAILABLE:
                return self._fallback_ai_reply(profile, message)

            body_analysis_text = ""
            try:
                if hasattr(self.db, 'get_latest_analysis'):
                    analysis = self.db.get_latest_analysis(username)
                    if analysis:
                        body_analysis_text = f"""
Body Analysis:
- Body Type: {analysis.get('body_type', 'Unknown')}
- Body Fat Percentage: {analysis.get('body_fat_percent', 'Unknown')}%
- Shoulder/Hip Ratio: {analysis.get('shoulder_hip_ratio', 'Unknown')}
- Suggested Goal: {analysis.get('suggested_goal', 'Unknown')}
"""
            except Exception as e:
                print(f"Warning: Could not retrieve body analysis: {e}")

            injuries = profile.get('injuries', 'None')
            allergies = profile.get('allergies', 'None')

            system_prompt = f"""You are an expert AI personal trainer and nutritionist. Use the user's profile and body analysis data below to give personalized, helpful advice.

User Profile:
- Height: {profile.get('height', 'Unknown')} cm
- Weight: {profile.get('weight', 'Unknown')} kg
- Age: {profile.get('age', 'Unknown')} years
- Gender: {profile.get('gender', 'Unknown')}
- Goal: {profile.get('goal', 'Unknown')}
- Training days: {profile.get('training_days', 'Unknown')} per week
- Activity level: {profile.get('activity_level', 'Unknown')}
- Injuries: {injuries}
- Food Allergies: {allergies}
{body_analysis_text}

Guidelines:
- Be encouraging and friendly. Use emojis occasionally.
- Give practical, actionable advice.
- Keep responses concise (max 4-5 sentences unless asked for details).
- If asked about exercises, prioritize safety and proper form, especially considering user's injuries.
- If the user's goal is unknown, ask them to choose one.
- Answer in English.

User question: {message}

Your response:"""

            response = ollama.chat(
                model='mistral:7b-instruct-q4_0',
                messages=[
                    {'role': 'system', 'content': system_prompt},
                    {'role': 'user', 'content': message}
                ]
            )

            return response['message']['content']

        except Exception as e:
            print(f"AI Error: {e}")
            return self._fallback_ai_reply(session.get('profile_data', {}), message)

    def _fallback_ai_reply(self, profile, message):
        goal = profile.get('goal', 'stay fit')
        injuries = profile.get('injuries', '')

        warning = ""
        if injuries:
            warning = " Considering your injuries, use controlled movement and stop if pain increases."

        return (
            f"I can still help without cloud AI. Based on your goal ({goal}), focus on progressive overload, "
            f"protein intake, and consistent sleep (7-9h). For this question: '{message}', start with "
            f"2-3 focused sessions this week, track reps/weights, and adjust calories slowly each week.{warning}"
        )
