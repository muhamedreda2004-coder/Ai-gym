import pandas as pd
import random

class ExerciseAlgorithm:
    def __init__(self, excel_path):
        self.exercises = []
        self.body_parts = {}
        self.load_exercises(excel_path)
    
    def load_exercises(self, excel_path):
        try:
            df = pd.read_excel(excel_path)
            for _, row in df.iterrows():
                sets_min, sets_max = self._parse_sets(str(row['Sets']))
                reps_min, reps_max = self._parse_reps(str(row['Reps per Set']))
                
                exercise = {
                    'body_part': row['Body Part'],
                    'muscle': row['Type of Muscle'],
                    'name': row['Workout'],
                    'sets_min': sets_min,
                    'sets_max': sets_max,
                    'reps_min': reps_min,
                    'reps_max': reps_max
                }
                self.exercises.append(exercise)
                
                if exercise['body_part'] not in self.body_parts:
                    self.body_parts[exercise['body_part']] = []
                self.body_parts[exercise['body_part']].append(exercise)
            
            print(f"✅ Loaded {len(self.exercises)} exercises")
        except Exception as e:
            print(f"⚠️ Error loading exercises: {e}")
    
    def _parse_sets(self, sets_str):
        sets_str = sets_str.lower()
        if 'sets of' in sets_str:
            parts = sets_str.split('sets of')
            try:
                s_min = int(parts[0].strip())
                return s_min, s_min
            except:
                return 3, 4
        elif '-' in sets_str:
            parts = sets_str.split('-')
            try:
                return int(parts[0]), int(parts[1])
            except:
                return 3, 4
        elif 'seconds' in sets_str or 'sec' in sets_str:
            return 3, 4
        else:
            try:
                s = int(sets_str)
                return s, s
            except:
                return 3, 4
    
    def _parse_reps(self, reps_str):
        reps_str = reps_str.lower()
        if 'seconds' in reps_str or 'sec' in reps_str:
            nums = [int(s) for s in reps_str.split() if s.isdigit()]
            if nums:
                return nums[0], nums[0] + 30
            return 30, 60
        elif '-' in reps_str:
            parts = reps_str.split('-')
            try:
                return int(parts[0]), int(parts[1])
            except:
                return 8, 12
        else:
            try:
                r = int(reps_str)
                return r, r
            except:
                return 8, 12
    
    def get_by_body_part(self, body_part):
        return self.body_parts.get(body_part, [])
    
    def get_chest_exercises(self):
        return self.get_by_body_part('Chest')
    
    def get_back_exercises(self):
        return self.get_by_body_part('Back')
    
    def get_legs_exercises(self):
        return self.get_by_body_part('Legs')
    
    def get_shoulders_exercises(self):
        return self.get_by_body_part('Shoulders')
    
    def get_arms_exercises(self):
        return self.get_by_body_part('Arms')
    
    def get_abs_exercises(self):
        return self.get_by_body_part('Abs')
    
    def generate_workout_plan(self, user_data):
        days_per_week = int(user_data.get('training_days', 3))
        goal = user_data.get('goal', 'stay fit').lower()
        
        if 'lose' in goal:
            rep_range = "15-20"
            rest_time = "30-45 seconds"
            focus = "🔥 Fat Loss & Endurance"
        elif 'gain' in goal:
            rep_range = "8-12"
            rest_time = "60-90 seconds"
            focus = "💪 Muscle Building"
        else:
            rep_range = "12-15"
            rest_time = "45-60 seconds"
            focus = "⚖️ General Fitness"
        
        if days_per_week == 3:
            splits = [
                {"name": "Full Body A", "exercises": self._create_full_body_workout()},
                {"name": "Full Body B", "exercises": self._create_full_body_workout(variation=True)},
                {"name": "Full Body C", "exercises": self._create_full_body_workout(variation=True)}
            ]
        elif days_per_week == 4:
            splits = [
                {"name": "Upper Body", "exercises": self._create_upper_body_workout()},
                {"name": "Lower Body", "exercises": self._create_lower_body_workout()},
                {"name": "Upper Body", "exercises": self._create_upper_body_workout(variation=True)},
                {"name": "Lower Body", "exercises": self._create_lower_body_workout(variation=True)}
            ]
        else:
            splits = [
                {"name": "Chest & Triceps", "exercises": self._create_push_workout()},
                {"name": "Back & Biceps", "exercises": self._create_pull_workout()},
                {"name": "Legs", "exercises": self._create_legs_workout()},
                {"name": "Shoulders & Abs", "exercises": self._create_shoulders_workout()},
                {"name": "Full Body / Cardio", "exercises": self._create_full_body_workout()}
            ]
        
        plan = f"""💪 **{focus} - {days_per_week}-Day Split**

**Guidelines:**
• Reps: {rep_range} per set
• Rest: {rest_time} between sets
• Warm-up: 5-10 minutes cardio + dynamic stretches

"""
        for i, split in enumerate(splits[:days_per_week], 1):
            plan += f"\n**Day {i}: {split['name']}**\n"
            for ex in split['exercises'][:6]:
                plan += f"• {ex['name']}: {ex.get('sets', '3-4')} x {rep_range}\n"
        
        plan += f"""

**Cardio:**
• {self._get_cardio_recommendation(goal)}
"""
        return plan
    
    def _create_full_body_workout(self, variation=False):
        exercises = []
        if variation:
            exercises.extend([
                {"name": "Deadlifts", "sets": "3-4"},
                {"name": "Pull-ups", "sets": "3-4"},
                {"name": "Overhead Press", "sets": "3-4"}
            ])
        else:
            exercises.extend([
                {"name": "Barbell Squats", "sets": "3-4"},
                {"name": "Bench Press", "sets": "3-4"},
                {"name": "Barbell Rows", "sets": "3-4"}
            ])
        exercises.extend([
            {"name": "Leg Press", "sets": "3"},
            {"name": "Dumbbell Lunges", "sets": "3"},
            {"name": "Plank", "sets": "3"}
        ])
        return exercises
    
    def _create_upper_body_workout(self, variation=False):
        if variation:
            return [
                {"name": "Incline Dumbbell Press", "sets": "3-4"},
                {"name": "Seated Cable Rows", "sets": "3-4"},
                {"name": "Dumbbell Shoulder Press", "sets": "3-4"},
                {"name": "Lat Pulldowns", "sets": "3"},
                {"name": "Dumbbell Curls", "sets": "3"},
                {"name": "Triceps Pushdowns", "sets": "3"}
            ]
        else:
            return [
                {"name": "Barbell Bench Press", "sets": "3-4"},
                {"name": "Pull-ups", "sets": "3-4"},
                {"name": "Standing Military Press", "sets": "3-4"},
                {"name": "Bent Over Rows", "sets": "3"},
                {"name": "Hammer Curls", "sets": "3"},
                {"name": "Skull Crushers", "sets": "3"}
            ]
    
    def _create_lower_body_workout(self, variation=False):
        if variation:
            return [
                {"name": "Romanian Deadlifts", "sets": "3-4"},
                {"name": "Leg Press", "sets": "3-4"},
                {"name": "Walking Lunges", "sets": "3"},
                {"name": "Leg Curls", "sets": "3"},
                {"name": "Standing Calf Raises", "sets": "4"},
                {"name": "Hanging Leg Raises", "sets": "3"}
            ]
        else:
            return [
                {"name": "Barbell Squats", "sets": "3-4"},
                {"name": "Deadlifts", "sets": "3-4"},
                {"name": "Leg Extensions", "sets": "3"},
                {"name": "Glute Bridges", "sets": "3"},
                {"name": "Seated Calf Raises", "sets": "4"},
                {"name": "Russian Twists", "sets": "3"}
            ]
    
    def _create_push_workout(self):
        return [
            {"name": "Barbell Bench Press", "sets": "3-4"},
            {"name": "Incline Dumbbell Press", "sets": "3-4"},
            {"name": "Overhead Press", "sets": "3-4"},
            {"name": "Lateral Raises", "sets": "3"},
            {"name": "Triceps Dips", "sets": "3"},
            {"name": "Cable Crossovers", "sets": "3"}
        ]
    
    def _create_pull_workout(self):
        return [
            {"name": "Pull-ups", "sets": "3-4"},
            {"name": "Barbell Rows", "sets": "3-4"},
            {"name": "Face Pulls", "sets": "3-4"},
            {"name": "Dumbbell Curls", "sets": "3"},
            {"name": "Hammer Curls", "sets": "3"},
            {"name": "Deadlifts", "sets": "3"}
        ]
    
    def _create_legs_workout(self):
        return [
            {"name": "Barbell Squats", "sets": "4"},
            {"name": "Romanian Deadlifts", "sets": "3-4"},
            {"name": "Leg Press", "sets": "3"},
            {"name": "Leg Extensions", "sets": "3"},
            {"name": "Leg Curls", "sets": "3"},
            {"name": "Calf Raises", "sets": "4"}
        ]
    
    def _create_shoulders_workout(self):
        return [
            {"name": "Military Press", "sets": "3-4"},
            {"name": "Lateral Raises", "sets": "3-4"},
            {"name": "Bent Over Lateral Raises", "sets": "3-4"},
            {"name": "Face Pulls", "sets": "3"},
            {"name": "Crunches", "sets": "3"},
            {"name": "Plank", "sets": "3"}
        ]
    
    def _get_cardio_recommendation(self, goal):
        if 'lose' in goal:
            return "20-30 minutes moderate cardio after workouts + 1-2 dedicated cardio sessions weekly"
        elif 'gain' in goal:
            return "10-15 minutes light cardio for warm-up only, focus on weight training"
        else:
            return "15-20 minutes cardio after workouts, 2-3 times weekly"
    
    def get_exercise_details(self, exercise_name):
        for ex in self.exercises:
            if exercise_name.lower() in ex['name'].lower():
                return {
                    'name': ex['name'],
                    'body_part': ex['body_part'],
                    'muscle': ex['muscle'],
                    'sets': f"{ex['sets_min']}-{ex['sets_max']}",
                    'reps': f"{ex['reps_min']}-{ex['reps_max']}"
                }
        return None