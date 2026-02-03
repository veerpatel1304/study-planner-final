from datetime import datetime, timedelta
import random
import re
from pypdf import PdfReader

class StudyAgent:
    """
    An advanced Study Agent with robust PDF Syllabus parsing and ML-based difficulty prediction.
    """
    def __init__(self):
        self.difficulty_map = {
            '1': {'label': 'Easy', 'weight': 1, 'days': 1},
            '2': {'label': 'Medium', 'weight': 2, 'days': 2},
            '3': {'label': 'Hard', 'weight': 4, 'days': 3}
        }
        
        # Keywords for difficulty prediction
        self.hard_keywords = ['advanced', 'optimization', 'complexity', 'quantum', 'dynamics', 'stochastic', 'inference', 'analysis', 'theory', 'synthesis', 'design', 'distributed', 'compiler', 'neural', 'cryptography']
        self.medium_keywords = ['application', 'integration', 'structure', 'function', 'system', 'mechanism', 'logic', 'model', 'database', 'network', 'algorithm', 'software']

        # Noise patterns to ignore in PDF
        self.noise_patterns = [
            r'page\s*\d+', 
            r'subject\s*code', 
            r'bachelor\s*of', 
            r'semester', 
            r'w\.e\.f', 
            r'ay\s*\d+', 
            r'university', 
            r'teaching\s*and\s*examination',
            r'credit',
            r'marks',
            r'total\s*hours',
            r'list\s*of\s*experiments',
            r'session',
            r'course\s*outcome'
        ]

    def predict_difficulty(self, topic_name):
        """Simulates ML prediction based on keyword complexity"""
        score = 0
        name_lower = topic_name.lower()
        
        for word in self.hard_keywords:
            if word in name_lower: score += 1.5
        for word in self.medium_keywords:
            if word in name_lower: score += 0.5
            
        if len(topic_name.split()) > 6: score += 0.5
        
        if score >= 2: return '3'
        if score >= 0.7: return '2'
        return '1'

    def is_noise(self, text):
        """Checks if a line is likely administrative noise"""
        clean_text = text.lower().strip()
        if not clean_text: return True
        if len(clean_text) < 5: return True
        if clean_text.isdigit(): return True
        
        for pattern in self.noise_patterns:
            if re.search(pattern, clean_text):
                return True
        return False

    def extract_from_pdf(self, pdf_file, unit_start=None, unit_end=None):
        """
        Refined PDF parser that extracts meaningful Syllabus content and References.
        """
        reader = PdfReader(pdf_file)
        full_text = ""
        for page in reader.pages:
            full_text += page.extract_text() + "\n"

        # 1. Identify Reference section
        references = []
        ref_match = re.search(r'(?i)(text\s*books?|reference\s*books?|references)(.*)', full_text, re.DOTALL)
        if ref_match:
            ref_content = ref_match.group(2)
            # Take the first 5 distinct lines as references
            for line in ref_content.split('\n')[:10]:
                clean_ref = line.strip()
                if len(clean_ref) > 15 and not self.is_noise(clean_ref):
                    references.append(clean_ref)
        
        # 2. Extract Syllabus Units
        # Split by Unit/Module/Chapter markers
        unit_blocks = re.split(r'(?i)(unit|module|chapter)\s*[:\-\s]*([IVXLC\d]+)', full_text)
        
        extracted_topics = []
        
        # re.split with groups returns [pre-match, marker, num, post-match, marker, num, ...]
        i = 1
        while i < len(unit_blocks):
            marker = unit_blocks[i]
            num_str = unit_blocks[i+1]
            content = unit_blocks[i+2]
            
            num = self._to_int(num_str)
            
            try:
                if unit_start and str(unit_start).strip() and num < int(unit_start): 
                    i += 3
                    continue
                if unit_end and str(unit_end).strip() and num > int(unit_end):
                    i += 3
                    continue
            except: pass

            unit_label = f"Unit {num}"
            
            lines = content.split('\n')
            for line in lines:
                topic = line.strip()
                topic = re.sub(r'^(\d+\.|\*|\-|\u2022)\s*', '', topic)
                
                if len(topic) > 12 and not self.is_noise(topic):
                    if topic.lower().startswith('unit') and len(topic) < 20: continue
                    
                    extracted_topics.append({
                        'name': f"{unit_label}: {topic}",
                        'difficulty': self.predict_difficulty(topic),
                        'reference': random.choice(references) if references else None
                    })
            
            i += 3

        if not extracted_topics:
            syllabus_search = re.search(r'(?i)(syllabus|content|topics)(.*)', full_text, re.DOTALL)
            if syllabus_search:
                content = syllabus_search.group(2)
                for line in content.split('\n')[:40]:
                    topic = line.strip()
                    if len(topic) > 15 and not self.is_noise(topic):
                        extracted_topics.append({
                            'name': topic,
                            'difficulty': self.predict_difficulty(topic),
                            'reference': random.choice(references) if references else None
                        })

        return extracted_topics[:35]

    def _to_int(self, s):
        """Helper to convert various number formats to int"""
        s = s.upper().strip()
        if s.isdigit(): return int(s)
        romans = {'I':1, 'II':2, 'III':3, 'IV':4, 'V':5, 'VI':6, 'VII':7, 'VIII':8, 'IX':9, 'X':10}
        return romans.get(s, 0)

    def generate_plan(self, subjects_info, start_date_str, end_date_str):
        """
        AI-driven logic with balanced subject interleaving and manageable daily tasks.
        """
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
        except:
            start_date = datetime.fromisoformat(start_date_str[:10])
            end_date = datetime.fromisoformat(end_date_str[:10])

        total_days = (end_date - start_date).days + 1
        if total_days <= 0: return []

        # Group tasks by subject to allow interleaving
        subject_queues = {}
        for sub in subjects_info:
            sub_name = sub['name']
            if sub_name not in subject_queues:
                subject_queues[sub_name] = []
                
            raw_topics = sub.get('topics', '')
            if isinstance(raw_topics, list):
                topics_list = raw_topics
            else:
                raw_split = raw_topics.split(',')
                topics_list = [{'name': t.strip(), 'difficulty': sub.get('difficulty', '2'), 'reference': None} for t in raw_split if t.strip()]
            
            if not topics_list:
                topics_list = [{'name': f"Fundamentals of {sub_name}", 'difficulty': '2', 'reference': None}]

            for t_item in topics_list:
                name = t_item['name']
                diff = t_item.get('difficulty', sub.get('difficulty', '2'))
                ref = t_item.get('reference') 
                config = self.difficulty_map.get(diff, self.difficulty_map['2'])
                
                for i in range(config['days']):
                    subject_queues[sub_name].append({
                        'subject': sub_name,
                        'topic': name,
                        'difficulty': diff,
                        'reference': ref,
                        'day_num': i + 1,
                        'total_days': config['days']
                    })

        schedule = []
        subject_names = list(subject_queues.keys())
        if not subject_names: return []

        # Determine total tasks and target density
        all_tasks_count = sum(len(q) for q in subject_queues.values())
        # Cap tasks per day between 3 and 6 for efficiency
        tasks_per_day = min(6, max(3, all_tasks_count // total_days + 1))
        
        # Interleaving logic: Round-robin through subject queues
        current_day_offset = 0
        
        for day in range(total_days):
            current_date = start_date + timedelta(days=day)
            tasks_added_today = 0
            
            # Rotation logic to ensure subject mixing
            # We start from a different subject each day to balance it
            start_sub_idx = day % len(subject_names)
            
            # Try to fill tasks for the day
            attempts = 0
            while tasks_added_today < tasks_per_day and attempts < (len(subject_names) * 2):
                sub_idx = (start_sub_idx + attempts) % len(subject_names)
                target_sub = subject_names[sub_idx]
                
                if subject_queues[target_sub]:
                    item = subject_queues[target_sub].pop(0)
                    
                    diff_label = self.difficulty_map[item['difficulty']]['label']
                    task_desc = item['topic']
                    if item['total_days'] > 1:
                        task_desc += f" (Part {item['day_num']}/{item['total_days']})"
                    
                    # Generate reference link
                    topic_clean = item['topic'].replace(':', '').strip()
                    if item['reference']:
                        ref_query = item['reference'].replace(' ', '+')
                        ref_link = f"https://www.google.com/search?q={ref_query}+free+pdf+book"
                        ref_label = f"Ref: {item['reference']}"
                    else:
                        query = f"{item['subject']}+{topic_clean}".replace(' ', '+')
                        ref_link = f"https://www.google.com/search?q={query}+tutorial+free+course"
                        ref_label = "Search free courses & materials"

                    schedule.append({
                        "date": current_date.strftime('%Y-%m-%d'),
                        "subject": item['subject'],
                        "description": f"[{diff_label}] {task_desc}",
                        "reference_url": ref_link,
                        "reference_text": ref_label,
                        "difficulty": item['difficulty']
                    })
                    tasks_added_today += 1
                attempts += 1
            
            # If no tasks left anywhere, break early
            if all(not q for q in subject_queues.values()):
                break

        return schedule

def get_agent():
    return StudyAgent()
