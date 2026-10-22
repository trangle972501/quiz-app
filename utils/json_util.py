import json 
import random
import math
import os
from pathlib import Path

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "data", "{exam}", "{exam_type}", "{lang}", "quiz_data.json")

class JsonUtil:

    @classmethod
    def load_quiz_data(cls, exam: str, exam_type: str, lang: str = "en") -> dict:
        try:
            file_path = DATA_PATH.format(exam=exam, exam_type=exam_type, lang=lang)
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Quiz data not found: {file_path}")
            return None



    @classmethod  
    def chunk_exams(cls, exam: str, exam_type: str, lang: str = "en"):
        # Group questions into chunks of <target_count> to form seperate exams
        target_count = 40
        try:
            all_questions = cls.load_quiz_data(exam, exam_type, lang)
            if not all_questions:
                return {}
            exams_pool = {}
            total_available = len(all_questions)

            #Calaculate how many full exams we can make from unique questions
            num_exams = max(1, math.ceil(total_available / target_count))
            print(f"Total available questions: {total_available}, Target count per exam: {target_count}, Number of exams: {num_exams}")

            for i in range(num_exams):
                start_idx = i * target_count
                end_idx = start_idx + target_count
                chunk = all_questions[start_idx:end_idx]

                # Rule: if a chunk is shorter than target_count, resuse previous questions to fill it up
                if len(chunk) < target_count and total_available > 0:
                    needed = target_count - len(chunk)
                    chunk.extend(random.choices(chunk, k=needed))
                exams_pool[f"Exam {i + 1} ({target_count} Questions)"] = chunk

            return exams_pool
        except:
            return None