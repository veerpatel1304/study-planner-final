from datetime import datetime, timedelta
import random
import re
from pypdf import PdfReader

class StudyAgent:
    """
    An advanced Study Agent with PDF Syllabus parsing and ML-based difficulty prediction.
    """
    def __init__(self):
        self.difficulty_map = {
            '1': {'label': 'Easy', 'weight': 1, 'days': 1},
            '2': {'label': 'Medium', 'weight': 2, 'days': 2},
            '3': {'label': 'Hard', 'weight': 4, 'days': 3}
        }
        
        # Hard keywords for "ML" prediction
        self.hard_keywords = ['advanced', 'optimization', 'complexity', 'quantum', 'dynamics', 'stochastic', 'inference', 'analysis', 'theory', 'synthesis', 'design']
        self.medium_keywords = ['application', 'integration', 'structure', 'function', 'system', 'mechanism', 'logic', 'model']

    def predict_difficulty(self, topic_name):
        """Simulates ML prediction based on keyword complexity and length"""
        score = 0
        name_lower = topic_name.lower()
        
        # Heuristic rules representing a simplified 'ML' model
        for word in self.hard_keywords:
            if word in name_lower: score += 1.5
        for word in self.medium_keywords:
            if word in name_lower: score += 0.5
            
        if len(topic_name.split()) > 5: score += 0.5 # Long complex names
        
        if score >= 2: return '3' # Hard
        if score >= 0.7: return '2' # Medium
        return '1' # Easy

    def extract_from_pdf(self, pdf_file, unit_start=None, unit_end=None):
        """
        Parses PDF and extracts topics linked to Units.
        """
        reader = PdfReader(pdf_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"

        # Basic Units extraction logic
        # Looking for things like "Unit 1", "Module 2", "Chapter 3"
        units = re.split(r'(?i)unit|module|chapter', text)
        extracted_topics = []
        
        current_unit_num = 0
        for unit_content in units:
            if not unit_content.strip(): continue
            
            # Try to catch the number following 'unit'
            match = re.search(r'^\s*(\d+)', unit_content)
            if match:
                current_unit_num = int(match.group(1))
            else:
                current_unit_num += 1
            
            # Filter by unit range if provided
            if unit_start and current_unit_num < int(unit_start): continue
            if unit_end and current_unit_num > int(unit_end): continue
            
            # Extract lines as topics
            lines = unit_content.split('\n')
            for line in lines:
                clean_line = line.strip()
                if len(clean_line) > 10 and not clean_line.isdigit():
                    # Predict difficulty
                    extracted_topics.append({
                        'name': f"Unit {current_unit_num}: {clean_line[:60]}...",
                        'difficulty': self.predict_difficulty(clean_line)
                    })
        
        return extracted_topics[:30] # Limit to 30 topics for safety

    def generate_plan(self, subjects_info, start_date_str, end_date_str):
        """
        AI-driven logic with time allocation based on predicted difficulty.
        """
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
        except:
            start_date = datetime.fromisoformat(start_date_str[:10])
            end_date = datetime.fromisoformat(end_date_str[:10])

        total_days = (end_date - start_date).days + 1
        if total_days <= 0: return []

        # Build a master list of topics across all subjects
        # Each topic will be assigned a specific duration
        master_task_queue = []
        for sub in subjects_info:
            raw_topics = sub.get('topics', '').split(',')
            topics = [t.strip() for t in raw_topics if t.strip()]
            if not topics:
                topics = [f"Fundamentals of {sub['name']}"]

            for t_name in topics:
                # If difficulty not provided (PDF upload), predict it
                diff = sub.get('difficulty')
                if not diff:
                    diff = self.predict_difficulty(t_name)
                
                config = self.difficulty_map[diff]
                # A Hard topic gets 3 slots, Medium gets 2, Easy gets 1
                for i in range(config['days']):
                    master_task_queue.append({
                        'subject': sub['name'],
                        'topic': t_name,
                        'difficulty': diff,
                        'day_num': i + 1,
                        'total_days': config['days']
                    })

        schedule = []
        if not master_task_queue: return []

        # Distribute master_task_queue over available days
        # We aim for ~2-4 tasks per day
        tasks_per_day = max(2, len(master_task_queue) // total_days + 1)
        
        for day in range(total_days):
            current_date = start_date + timedelta(days=day)
            
            for _ in range(tasks_per_day):
                if not master_task_queue: break
                
                item = master_task_queue.pop(0)
                diff_label = self.difficulty_map[item['difficulty']]['label']
                
                task_desc = f"{item['topic']}"
                if item['total_days'] > 1:
                    task_desc += f" (Part {item['day_num']}/{item['total_days']})"
                
                schedule.append({
                    "date": current_date.strftime('%Y-%m-%d'),
                    "subject": item['subject'],
                    "description": f"[{diff_label}] {task_desc}",
                    "reference": f"Recommended: Search for '{item['topic']}' concepts",
                    "difficulty": item['difficulty']
                })

        return schedule

def get_agent():
    return StudyAgent()
