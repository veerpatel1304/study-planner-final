from flask import Flask, render_template, request, redirect, url_for, session, flash
from study_planner.database.db import get_db_connection
from datetime import datetime
import os

# Absolute path to the directory containing this file (the /api folder)
base_dir = os.path.dirname(os.path.abspath(__file__))

# Initialize Flask with specific folders in the study_planner directory
# We use absolute paths derived from base_dir to ensure it works on Vercel regardless of CWD
app = Flask(__name__, 
            template_folder=os.path.join(base_dir, '..', 'study_planner', 'templates'), 
            static_folder=os.path.join(base_dir, '..', 'study_planner', 'static'))

# Secret key is needed for session management
app.secret_key = os.environ.get('SECRET_KEY', 'your_secret_key_here')

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        try:
            supabase = get_db_connection()
            response = supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            session['user'] = response.user.email
            session['user_id'] = response.user.id 
            session['access_token'] = response.session.access_token
            
            flash("Login successful!", "success")
            return redirect(url_for('dashboard'))
            
        except Exception as e:
            error_msg = getattr(e, 'message', str(e))
            flash(f"Login failed: {error_msg}", "error")
        
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    try:
        supabase = get_db_connection()
        supabase.auth.sign_out()
    except:
        pass
    flash("You have been logged out.", "info")
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if password != confirm_password:
            flash("Passwords do not match!", "error")
            return render_template('register.html')
            
        try:
            supabase = get_db_connection()
            response = supabase.auth.sign_up({
                "email": email,
                "password": password,
                "options": {
                    "data": {
                        "full_name": name
                    }
                }
            })
            
            if response.user and response.user.identities == []:
                 flash("User already exists. Please login.", "info")
                 return redirect(url_for('login'))
            
            try:
                user_data = {
                    "id": response.user.id,
                    "email": email,
                    "full_name": name
                }
                supabase.table('users').insert(user_data).execute()
            except Exception as db_error:
                print(f"Database insertion error: {db_error}")

            if response.session:
                session['user'] = response.user.email
                session['user_id'] = response.user.id 
                session['access_token'] = response.session.access_token
                flash("Registration successful! Welcome.", "success")
                return redirect(url_for('dashboard'))
            else:
                flash("Registration successful! Please check your email to verify your account.", "success")
                return redirect(url_for('login'))
            
        except Exception as e:
            error_msg = getattr(e, 'message', str(e))
            flash(f"Registration failed: {error_msg}", "error")
            
    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        flash("Please login to access the dashboard.", "warning")
        return redirect(url_for('login'))
    
    plans = []
    today_tasks = []
    try:
        supabase = get_db_connection(session.get('access_token'))
        user_id = session.get('user_id')
        if user_id:
             response = supabase.table('study_plans').select("*").eq('user_id', user_id).order('created_at', desc=True).execute()
             plans = response.data
             
             if plans:
                 plan_ids = [p['id'] for p in plans]
                 today_str = datetime.now().date().isoformat()
                 
                 subjects_res = supabase.table('subjects').select("id, name").in_('plan_id', plan_ids).execute()
                 if subjects_res.data:
                     sub_ids = [s['id'] for s in subjects_res.data]
                     sub_map = {s['id']: s['name'] for s in subjects_res.data}
                     
                     tasks_res = supabase.table('tasks').select("*").in_('subject_id', sub_ids).eq('due_date', today_str).execute()
                     today_tasks = tasks_res.data
                     
                     for task in today_tasks:
                         task['subject_name'] = sub_map.get(task['subject_id'], "Unknown")

    except Exception as e:
        print(f"Error fetching dashboard data: {e}")
        
    db_healthy = True
    try:
        supabase = get_db_connection(session.get('access_token'))
        supabase.table('profiles').select("id").limit(1).execute()
        supabase.table('tasks').select("id").limit(1).execute()
    except Exception as e:
        if "PGRST204" in str(e) or "404" in str(e) or "tasks" in str(e).lower():
            db_healthy = False

    return render_template('dashboard.html', 
                           user=session['user'], 
                           plans=plans, 
                           today_tasks=today_tasks,
                           db_healthy=db_healthy)

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    supabase = get_db_connection(session.get('access_token'))
    user_id = session.get('user_id')
    
    if not user_id:
        flash("Session expired. Please login again.", "warning")
        return redirect(url_for('logout'))
        
    try:
        if request.method == 'POST':
            profile_data = {
                "id": user_id, 
                "full_name": request.form.get('full_name'),
                "university": request.form.get('university'),
                "degree": request.form.get('degree'),
                "major": request.form.get('major'),
                "current_semester": int(request.form.get('current_semester')) if request.form.get('current_semester') else 0,
                "graduation_year": int(request.form.get('graduation_year')) if request.form.get('graduation_year') else None
            }
            supabase.table('profiles').upsert(profile_data).execute()
            flash("Profile updated successfully!", "success")
            return redirect(url_for('profile'))
            
        profile_response = supabase.table('profiles').select("*").eq('id', user_id).execute()
        profile = profile_response.data[0] if profile_response.data else None
        return render_template('profile.html', profile=profile)
        
    except Exception as e:
        flash(f"Error accessing profile: {str(e)}", "error")
        return redirect(url_for('dashboard'))

@app.route('/create_plan', methods=['GET', 'POST'])
def create_plan():
    if 'user' not in session:
        return redirect(url_for('login'))
        
    if request.method == 'POST':
        title = request.form.get('title')
        goal = request.form.get('goal')
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        user_id = session.get('user_id')
        
        try:
            from study_planner.ai_planner import get_agent
            planner = get_agent()
            supabase = get_db_connection(session.get('access_token'))
            
            plan_data = {
                "user_id": user_id,
                "title": title,
                "goal": goal,
                "start_date": start_date,
                "end_date": end_date
            }
            plan_res = supabase.table('study_plans').insert(plan_data).execute()
            
            if not plan_res.data:
                raise Exception("Failed to create plan record")
                
            plan_id = plan_res.data[0]['id']
            subjects_data = []
            subjects_info_for_ai = [] 
            
            subjects = request.form.getlist('subjects[]')
            manual_topics_list = request.form.getlist('topics[]')
            difficulties = request.form.getlist('difficulties[]')
            unit_starts = request.form.getlist('unit_starts[]')
            unit_ends = request.form.getlist('unit_ends[]')
            syllabus_files = request.files.getlist('syllabus_pdfs[]')
            
            for i in range(len(subjects)):
                if not subjects[i].strip(): continue
                
                sub_name = subjects[i].strip()
                sub_diff = difficulties[i] if i < len(difficulties) else "2"
                manual_top = manual_topics_list[i].strip() if i < len(manual_topics_list) else ""
                file = syllabus_files[i] if i < len(syllabus_files) else None
                
                extracted_topics = []
                if file and file.filename != '':
                    u_start = unit_starts[i] if i < len(unit_starts) else None
                    u_end = unit_ends[i] if i < len(unit_ends) else None
                    extracted_topics = planner.extract_from_pdf(file, u_start, u_end)
                    
                main_topics_summary = manual_top
                if extracted_topics:
                    pdf_summary = f"Extracted {len(extracted_topics)} topics from PDF"
                    main_topics_summary = f"{manual_top}, {pdf_summary}" if manual_top else pdf_summary
                
                subjects_data.append({
                    "plan_id": plan_id,
                    "name": sub_name,
                    "topics": main_topics_summary
                })
                
                for t in extracted_topics:
                    subjects_info_for_ai.append({
                        'name': sub_name,
                        'topics': t['name'],
                        'difficulty': t['difficulty'],
                        'reference': t.get('reference')
                    })
                
                if manual_top:
                    for t in manual_top.split(','):
                        t_name = t.strip()
                        if t_name:
                            subjects_info_for_ai.append({
                                'name': sub_name,
                                'topics': t_name,
                                'difficulty': sub_diff
                            })
                            
            if subjects_data:
                sub_res = supabase.table('subjects').insert(subjects_data).execute()
                created_subjects = sub_res.data
                
                if not created_subjects:
                    raise Exception("Failed to save subjects to database.")
                
                subject_name_to_id = {s['name']: s['id'] for s in created_subjects}
                generated_schedule = planner.generate_plan(subjects_info_for_ai, start_date, end_date)
                
                tasks_data = []
                for item in generated_schedule:
                    s_id = subject_name_to_id.get(item['subject'])
                    if s_id:
                        tasks_data.append({
                            "subject_id": s_id,
                            "description": item['description'],
                            "reference": f"{item['reference_text']}|{item['reference_url']}",
                            "due_date": item['date'],
                            "is_completed": False
                        })
                
                if tasks_data:
                    try:
                        supabase.table('tasks').insert(tasks_data).execute()
                    except Exception as e:
                        if "PGRST205" in str(e) or "tasks" in str(e).lower():
                            flash("Plan created, but 'tasks' table is missing.", "warning")
                        else:
                            raise e
                
            flash("Study Plan created! AI has generated your schedule.", "success")
            return redirect(url_for('dashboard'))
            
        except Exception as e:
            flash(f"Error creating plan: {str(e)}", "error")
            return redirect(url_for('create_plan'))
            
    return render_template('create_plan.html')

@app.route('/view_plan/<plan_id>')
def view_plan(plan_id):
    if 'user' not in session:
        return redirect(url_for('login'))
        
    try:
        supabase = get_db_connection(session.get('access_token'))
        plan_res = supabase.table('study_plans').select("*").eq('id', plan_id).single().execute()
        plan = plan_res.data
        
        subjects_res = supabase.table('subjects').select("id, name").eq('plan_id', plan_id).execute()
        subject_ids = [s['id'] for s in subjects_res.data]
        subject_map = {s['id']: s['name'] for s in subjects_res.data}
        
        if not subject_ids:
            return render_template('view_plan.html', plan=plan, tasks_by_date={}, sorted_dates=[])

        tasks_by_date = {}
        try:
            tasks_res = supabase.table('tasks').select("*").in_('subject_id', subject_ids).order('due_date', desc=False).execute()
            for task in tasks_res.data:
                task['subjects'] = {'name': subject_map.get(task['subject_id'], "Unknown Subject")}
                date = task['due_date']
                if date not in tasks_by_date:
                    tasks_by_date[date] = []
                tasks_by_date[date].append(task)
        except Exception as e:
            if "PGRST205" in str(e) or "tasks" in str(e).lower():
                flash("The 'tasks' table is missing in your database.", "warning")
            else:
                raise e
            
        sorted_dates = sorted(tasks_by_date.keys())
        return render_template('view_plan.html', plan=plan, tasks_by_date=tasks_by_date, sorted_dates=sorted_dates)
        
    except Exception as e:
        flash(f"Error loading plan details: {str(e)}", "error")
        return redirect(url_for('dashboard'))

@app.route('/toggle_task/<task_id>', methods=['POST'])
def toggle_task(task_id):
    if 'user' not in session:
        return {"error": "Unauthorized"}, 401
    completed = request.json.get('completed', False)
    try:
        supabase = get_db_connection(session.get('access_token'))
        supabase.table('tasks').update({"is_completed": completed}).eq('id', task_id).execute()
        return {"success": True}
    except Exception as e:
        return {"error": str(e)}, 500

if __name__ == '__main__':
    app.run(debug=True)
