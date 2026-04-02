import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
import random
import warnings
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
warnings.filterwarnings('ignore')

class FoodAlgorithm:
    def __init__(self, csv_path):
        try:
            self.df = pd.read_csv(csv_path, on_bad_lines='skip', engine='python')
            print(f"✅ Loaded {len(self.df)} rows.")
        except Exception as e:
            print(f"❌ Error reading CSV: {e}")
            raise

        self._clean_data()
        self._prepare_features()
        self._build_and_train_model()
        print("✅ Food Algorithm with simple Deep Learning model ready")

    def _clean_data(self):
        rename_map = {
            'Food_Item': 'Food',
            'Calories (kcal)': 'Calories',
            'Protein (g)': 'Protein',
            'Carbohydrates (g)': 'Carbs',
            'Fat (g)': 'Fat',
            'Meal_Type': 'Meal_Type'
        }
        self.df.rename(columns=rename_map, inplace=True, errors='ignore')

        num_cols = ['Calories', 'Protein', 'Carbs', 'Fat']
        for col in num_cols:
            self.df[col] = pd.to_numeric(self.df[col], errors='coerce')

        self.df['Meal_Type'] = self.df['Meal_Type'].astype(str).str.strip()
        meal_map = {'Breakfast': 'Breakfast', 'Lunch': 'Lunch', 'Dinner': 'Dinner', 'Snack': 'Snack'}
        self.df['Meal_Type'] = self.df['Meal_Type'].map(meal_map).fillna('Snack')

        def to_str(x):
            if isinstance(x, (list, tuple)):
                return ' '.join(str(i) for i in x)
            return str(x)
        self.df['Food'] = self.df['Food'].apply(to_str).str.strip()
        self.df = self.df[self.df['Food'] != '']
        self.df = self.df.dropna(subset=['Calories', 'Protein', 'Carbs', 'Fat'])
        print(f"✅ Cleaned data: {len(self.df)} valid foods.")

    def _prepare_features(self):
        self.df['Protein_Ratio'] = self.df['Protein'] / (self.df['Calories'] + 1)
        self.df['Carbs_Ratio'] = self.df['Carbs'] / (self.df['Calories'] + 1)
        self.df['Fat_Ratio'] = self.df['Fat'] / (self.df['Calories'] + 1)

        self.meal_encoder = {'Breakfast': 0, 'Lunch': 1, 'Dinner': 2, 'Snack': 3}
        self.df['Meal_Code'] = self.df['Meal_Type'].map(self.meal_encoder).fillna(3)

        self.features = ['Calories', 'Protein', 'Carbs', 'Fat',
                         'Protein_Ratio', 'Carbs_Ratio', 'Fat_Ratio',
                         'Meal_Code']

        X_raw = self.df[self.features].fillna(0)
        self.scaler = StandardScaler()
        self.X_scaled = self.scaler.fit_transform(X_raw)

        quality = (self.df['Protein'] / (self.df['Calories'] + 1)) * 100
        quality = quality.clip(0, 100)
        self.y = quality + np.random.uniform(-5, 5, size=len(quality))
        self.y = self.y.clip(0, 100)

    def _build_and_train_model(self):
        model = keras.Sequential([
            layers.Dense(32, activation='relu', input_shape=(self.X_scaled.shape[1],)),
            layers.Dropout(0.2),
            layers.Dense(16, activation='relu'),
            layers.Dense(1)
        ])
        model.compile(optimizer='adam', loss='mse')
        model.fit(self.X_scaled, self.y, epochs=50, batch_size=16, verbose=0)
        self.model = model

    def _score_food(self, food_row):
        X = food_row[self.features].fillna(0).values.reshape(1, -1)
        X_scaled = self.scaler.transform(X)
        return float(self.model.predict(X_scaled, verbose=0)[0, 0])

    def calculate_needs(self, weight, height, age, gender, activity_level, goal):
        weight, height, age = float(weight), float(height), float(age)
        if gender.lower() == 'male':
            bmr = (10 * weight) + (6.25 * height) - (5 * age) + 5
        else:
            bmr = (10 * weight) + (6.25 * height) - (5 * age) - 161

        multipliers = {'sedentary': 1.2, 'light': 1.375, 'moderate': 1.55,
                       'active': 1.725, 'very active': 1.9}
        tdee = bmr * multipliers.get(activity_level.lower(), 1.55)

        if 'lose' in goal.lower():
            calories = tdee - 500
            protein = weight * 2.2
            carbs = weight * 2.5
            fat = weight * 0.7
        elif 'gain' in goal.lower():
            calories = tdee + 350
            protein = weight * 2.0
            carbs = weight * 4.5
            fat = weight * 1.0
        else:
            calories = tdee
            protein = weight * 1.8
            carbs = weight * 3.0
            fat = weight * 0.8

        return {
            'calories': round(calories),
            'protein': round(protein),
            'carbs': round(carbs),
            'fat': round(fat)
        }

    def _get_realistic_serving(self, food_name, base_calories, target_calories):
        food_lower = food_name.lower()
        high_calorie_foods = ['pizza', 'burger', 'lasagna', 'tacos', 'sandwich', 'pasta',
                              'risotto', 'curry', 'burrito', 'quesadilla', 'macaroni',
                              'grilled cheese', 'cheesecake', 'cake', 'pie', 'donut', 'cookie']
        is_high_calorie = any(f in food_lower for f in high_calorie_foods)

        serving_map = {
            'egg': (1, 'egg', [1, 2, 3], 70),
            'chicken': (100, 'g', [100, 150, 200], 165),
            'salmon': (100, 'g', [100, 150, 200], 230),
            'beef': (100, 'g', [100, 150, 200], 250),
            'steak': (100, 'g', [100, 150, 200], 250),
            'tofu': (100, 'g', [100, 150, 200], 90),
            'yogurt': (150, 'g', [150, 200], 100),
            'oatmeal': (40, 'g', [40, 60, 80], 150),
            'rice': (150, 'g', [100, 150], 130),
            'brown rice': (150, 'g', [100, 150], 140),
            'quinoa': (150, 'g', [100, 150], 140),
            'bread': (1, 'slice', [1, 2], 80),
            'toast': (1, 'slice', [1, 2], 80),
            'banana': (1, 'piece', [1], 105),
            'apple': (1, 'piece', [1], 95),
            'potato': (1, 'medium', [1], 160),
            'sweet potato': (1, 'medium', [1], 100),
            'salad': (150, 'g', [150, 200], 50),
            'soup': (250, 'g', [250], 150),
            'sandwich': (1, 'sandwich', [1], 350),
            'wrap': (1, 'wrap', [1], 400),
            'pancake': (1, 'pancake', [2, 3], 90),
            'waffle': (1, 'waffle', [2], 110),
            'protein shake': (1, 'scoop', [1], 120),
            'protein bar': (1, 'bar', [1], 210),
            'pizza': (1, 'slice', [1], 250),
            'burger': (1, 'burger', [1], 550),
            'lasagna': (1, 'piece', [1], 350),
            'taco': (1, 'taco', [1, 2], 190),
            'pasta': (150, 'g', [150], 200),
            'spaghetti': (150, 'g', [150], 200),
            'fries': (100, 'g', [100], 340),
            'chips': (30, 'g', [30], 160),
            'nuts': (30, 'g', [30], 180),
            'almond': (30, 'g', [30], 160),
        }
        for key, info in serving_map.items():
            if key in food_lower:
                servings = random.choice(info[2])
                if is_high_calorie and servings > 1:
                    servings = 1
                if info[1] == 'g':
                    grams = servings * info[0]
                    return f"{grams}g", grams
                return f"{servings} {info[1]}{'s' if servings > 1 else ''}", servings

        if base_calories > 400:
            grams = 100
        elif base_calories > 200:
            grams = random.choice([100, 150])
        else:
            grams = random.choice([150, 200])
        if (grams / 100) * base_calories > 600:
            grams = int(600 / base_calories * 100)
            grams = max(50, grams)
        return f"{grams}g", grams

    def _compatibility_score(self, food_row, targets):
        cal_diff = abs(food_row['Calories'] - targets['calories']) / max(targets['calories'], 1)
        pro_diff = abs(food_row['Protein'] - targets['protein']) / max(targets['protein'], 1)
        carb_diff = abs(food_row['Carbs'] - targets['carbs']) / max(targets['carbs'], 1)
        fat_diff = abs(food_row['Fat'] - targets['fat']) / max(targets['fat'], 1)
        macro_score = 100 - (cal_diff * 30 + pro_diff * 30 + carb_diff * 20 + fat_diff * 20)
        return max(0, min(100, macro_score))

    def find_foods(self, targets, meal_type, n=2, exclude_names=None):
        if exclude_names is None:
            exclude_names = []
        exclude_names = [str(x) for x in exclude_names]

        meal_foods = self.df[self.df['Meal_Type'] == meal_type]
        if len(meal_foods) == 0:
            meal_foods = self.df

        scored = []
        for _, row in meal_foods.iterrows():
            food_name = row['Food']
            if food_name in exclude_names:
                continue
            comp = self._compatibility_score(row, targets)
            quality = self._score_food(row)
            total = 0.6 * comp + 0.4 * quality
            scored.append((food_name, total))

        scored.sort(key=lambda x: x[1], reverse=True)
        top = min(6, len(scored))
        candidates = scored[:top]
        random.shuffle(candidates)

        selected = []
        for name, _ in candidates[:n]:
            food_row = self.df[self.df['Food'] == name].iloc[0]
            serving_text, grams = self._get_realistic_serving(name, food_row['Calories'], targets['calories'])
            ratio = grams / 100
            total_calories = food_row['Calories'] * ratio
            total_protein = food_row['Protein'] * ratio
            total_carbs = food_row['Carbs'] * ratio
            total_fat = food_row['Fat'] * ratio

            if total_calories > 700:
                ratio = 700 / food_row['Calories']
                grams = int(ratio * 100)
                total_calories = food_row['Calories'] * ratio
                total_protein = food_row['Protein'] * ratio
                total_carbs = food_row['Carbs'] * ratio
                total_fat = food_row['Fat'] * ratio
                serving_text = f"{grams}g"

            selected.append({
                'name': name,
                'serving': serving_text,
                'calories': round(total_calories),
                'protein': round(total_protein, 1),
                'carbs': round(total_carbs, 1),
                'fat': round(total_fat, 1)
            })
        return selected

    def generate_meal_plan(self, user_data, exclude_foods=None):
        if exclude_foods is None:
            exclude_foods = []

        needs = self.calculate_needs(
            user_data['weight'],
            user_data['height'],
            user_data['age'],
            user_data['gender'],
            user_data.get('activity_level', 'moderate'),
            user_data.get('goal', 'maintain')
        )

        meal_config = {
            'breakfast': {'ratio': 0.25, 'type': 'Breakfast'},
            'morning_snack': {'ratio': 0.10, 'type': 'Snack'},
            'lunch': {'ratio': 0.30, 'type': 'Lunch'},
            'afternoon_snack': {'ratio': 0.10, 'type': 'Snack'},
            'dinner': {'ratio': 0.25, 'type': 'Dinner'}
        }

        meal_names = {
            'breakfast': '🌅 Breakfast',
            'morning_snack': '🍎 Morning Snack',
            'lunch': '☀️ Lunch',
            'afternoon_snack': '🥜 Afternoon Snack',
            'dinner': '🌙 Dinner'
        }

        meals = {}
        for meal_key, config in meal_config.items():
            meal_cals = needs['calories'] * config['ratio']
            targets = {
                'calories': meal_cals,
                'protein': needs['protein'] * config['ratio'],
                'carbs': needs['carbs'] * config['ratio'],
                'fat': needs['fat'] * config['ratio']
            }
            foods = self.find_foods(targets, config['type'], n=2, exclude_names=exclude_foods)
            meals[meal_key] = {
                'name': meal_names[meal_key],
                'calories': round(meal_cals),
                'foods': foods
            }

        return {
            'daily_needs': needs,
            'meals': meals
        }