# AI Study Planner

A full-stack web application designed to help students organize their learning, track progress, and generate AI-driven study schedules.

## 🚀 Features
- **AI-Powered Schedule Generation**: Automatically creates a study plan from manual input or PDF syllabi.
- **Syllabus Parsing**: Smart extraction of units and topics from PDF documents.
- **Interactive Checklist**: Track daily learning targets directly on the dashboard.
- **Persistent Profiles**: Store your educational details and graduation goals.
- **Secure Authentication**: Powerded by Supabase Auth with RLS (Row Level Security).

## 🛠️ Tech Stack
- **Frontend**: HTML5, Vanilla CSS, JavaScript
- **Backend**: Flask (Python)
- **Database**: Supabase (PostgreSQL)
- **Authentication**: Supabase Auth
- **AI/LLM**: Custom Study Agent with PDF parsing (`pypdf`)
- **Deployment**: Vercel

## 📦 Deployment on Vercel
This repository is configured for easy deployment on Vercel.

1. **Prerequisites**:
   - A [Supabase](https://supabase.com/) project.
   - Run the SQL code in `schema.sql` within your Supabase SQL Editor.

2. **Setup**:
   - Push this code to a GitHub repository.
   - Import the repository into [Vercel](https://vercel.com/).
   - Add the following **Environment Variables** in Vercel:
     - `SUPABASE_URL`: Your Supabase Project URL.
     - `SUPABASE_KEY`: Your Supabase Anon/Public Key.

## 💻 Local Development
1. Clone the repository.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file with your `SUPABASE_URL` and `SUPABASE_KEY`.
4. Run the app:
   ```bash
   python app.py
   ```

## 📄 License
MIT License
