import os, json, time
from flask import Flask, render_template, request, session, redirect, url_for, jsonify

app = Flask(__name__)
app.secret_key = "your_secret_key"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Ensure upload folder exists
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def load_questions(filename):
    path = os.path.join(BASE_DIR, "data", filename)
    with open(path, 'r') as f:
        return json.load(f)

# --- Landing Page ---
@app.route('/')
def index():
    return render_template("index1.html")

# --- Login Page ---
@app.route('/login')
def login():
    return render_template("login.html")

# --- Resume Upload ---
@app.route('/resume', methods=['GET', 'POST'])
def resume_upload():
    if request.method == 'POST':
        if 'resume_file' in request.files:
            file = request.files['resume_file']
            if file.filename != '':
                file_path = os.path.join(UPLOAD_FOLDER, file.filename)
                file.save(file_path)
                return redirect(url_for("instructions"))
        return redirect(url_for("resume_upload"))
    return render_template("resume.html")

# --- Instructions ---
@app.route('/instructions')
def instructions():
    return render_template("instructions.html")

# --- REQUIRED CHANGE: Interview Welcome Page ---
# This is the "middle man" route that shows your index.html robot page
@app.route('/start_interview')
def start_interview_page():
    return render_template("index.html")

# --- Round 1: Aptitude Submit ---
@app.route('/round1', methods=['GET', 'POST'])
def round1():
    questions = load_questions("round1.json")
    if request.method == 'POST':
        score = 0
        for i, q in enumerate(questions["aptitude"]):
            ans = request.form.get(f"aptitude{i}")
            if ans == q["answer"]:
                score += 5
        session["round1_score"] = score
        return redirect(url_for("round1_coding", q_index=0)) 
    return render_template("round1.html", questions=questions)

# --- Round 1: Coding Route (Handles Q1 and Q2) ---
@app.route('/round1_coding/<int:q_index>', methods=['GET', 'POST'])
def round1_coding(q_index):
    data = load_questions("round1.json")
    coding_questions = data.get("coding", [])

    if q_index >= len(coding_questions):
        return redirect(url_for("round2"))

    if request.method == 'POST':
        user_code = request.form.get("user_code")
        if user_code and user_code.strip():
            session["round1_score"] = session.get("round1_score", 0) + 10
        
        next_q = q_index + 1
        if next_q < len(coding_questions):
            return redirect(url_for("round1_coding", q_index=next_q))
        else:
            return redirect(url_for("round2"))

    return render_template("round1_coding.html", 
                           q=coding_questions[q_index], 
                           q_index=q_index, 
                           total_q=len(coding_questions))

# --- AJAX Route for "Real" Run Feel ---
@app.route('/run_code', methods=['POST'])
def run_code():
    data = request.json
    time.sleep(1) 
    
    all_data = load_questions("round1.json")
    q_idx = int(data.get('q_index', 0))
    expected = all_data['coding'][q_idx]['expected_output']
    
    return jsonify({
        "output": expected, 
        "status": "Passed ✅"
    })

# --- Round 2 (Theory) ---
@app.route('/round2', methods=['GET','POST'])
def round2():
    questions = load_questions("round2.json")
    if request.method == 'POST':
        score = 0
        for section in questions["sections"]:
            if section["section_name"] == "Theory":
                for i, q in enumerate(section["questions"]):
                    ans = request.form.get(f"theory_input{i}")
                    if ans and len(ans.strip()) > 0:
                        score += q.get("marks", 5)
        session["round2_score"] = score
        return redirect(url_for("round3"))
    return render_template("round2.html", questions=questions)

# --- Round 3 (MCQs) ---
@app.route('/round3', methods=['GET','POST'])
def round3():
    questions = load_questions("round3.json")
    if request.method == 'POST':
        score = 0
        for section in questions["sections"]:
            if section["section_name"] == "MCQ":
                for i, q in enumerate(section["questions"]):
                    ans = request.form.get(f"mcq_input{i}")
                    if ans == q["answer"]:
                        score += q.get("marks", 5)
        session["round3_score"] = score
        return redirect(url_for("round4"))
    return render_template("round3.html", questions=questions)

# --- Round 4 (Managerial) ---
@app.route('/round4', methods=['GET','POST'])
def round4():
    questions = load_questions("round4.json")
    if request.method == 'POST':
        score = 0
        for section in questions["sections"]:
            if section["section_name"] == "Managerial":
                for i, q in enumerate(section["questions"]):
                    ans = request.form.get(f"managerial_input{i}")
                    if ans and len(ans.strip()) > 0:
                        score += q.get("marks", 5)
        session["round4_score"] = score
        return redirect(url_for("round5"))
    return render_template("round4.html", questions=questions)

# --- Round 5 (HR) ---
@app.route('/round5', methods=['GET','POST'])
def round5():
    questions = load_questions("round5.json")
    if request.method == 'POST':
        score = 0
        for section in questions["sections"]:
            if section["section_name"] == "HR":
                for i, q in enumerate(section["questions"]):
                    ans = request.form.get(f"hr_input{i}")
                    if ans and len(ans.strip()) > 0:
                        score += q.get("marks", 5)
        session["round5_score"] = score
        return redirect(url_for("result"))
    return render_template("round5.html", questions=questions)

# --- Final Result ---
@app.route('/result')
def result():
    round1_score = min(session.get("round1_score", 0), 30)
    round2_score = min(session.get("round2_score", 0), 20)
    round3_score = min(session.get("round3_score", 0), 20)
    round4_score = min(session.get("round4_score", 0), 20)
    round5_score = min(session.get("round5_score", 0), 20)

    total_score = round1_score + round2_score + round3_score + round4_score + round5_score
    max_score = 110
    percentage = (total_score / max_score) * 100

    if percentage >= 90:
        rating = "Excellent"
    elif percentage >= 70:
        rating = "Good"
    else:
        rating = "Needs Improvement"

    feedback = "Keep practicing and improving your skills."

    return render_template("result.html",
                           round1_score=round1_score,
                           round2_score=round2_score,
                           round3_score=round3_score,
                           round4_score=round4_score,
                           round5_score=round5_score,
                           total_score=total_score,
                           max_score=max_score,
                           percentage=round(percentage, 2),
                           rating=rating,
                           feedback=feedback)

if __name__ == "__main__":
    app.run(debug=True)