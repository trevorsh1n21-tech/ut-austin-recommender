from flask import Flask, request, jsonify
from flask_cors import CORS
import json

# ============================================
# 1. YOUR EXISTING LOGIC (Paste your full code here)
# ============================================
# IMPORTANT: Paste the ENTIRE content of your recommendation_engine.py 
# (COURSES, ROLES, UserProfile class, RecommendationEngine class) 
# BELOW this line, BEFORE the Flask app setup.

# --- START OF YOUR LOGIC ---
# (Paste your COURSES list, ROLES dict, UserProfile class, and RecommendationEngine class here)
# --- END OF YOUR LOGIC ---

# If you don't have the full code ready, here is a minimal version to test deployment:
COURSES = [
    {"course_id": "UT-AG-001", "title": "Post-Graduate Program in AI Agents & GenAI", "teaches_skills": ["Generative AI", "LLMs", "RAG", "AI Agents", "Security"], "url": "https://onlineexeced.mccombs.utexas.edu/post-graduate-program-in-ai-agents-and-generative-ai-for-business-applications", "duration_weeks": 12},
    {"course_id": "UT-GD-004", "title": "Generative AI for Software Development", "teaches_skills": ["JavaScript", "React", "Node.js", "Python", "API Dev"], "url": "https://onlineexeced.mccombs.utexas.edu/genai-for-software-development", "duration_weeks": 14}
]

ROLES = {
    "AI Solutions Architect": {"required_skills": ["Generative AI", "LLMs", "RAG", "AI Agents", "Security", "API Design"]},
    "Full-Stack AI Developer": {"required_skills": ["JavaScript", "React", "Node.js", "Python", "API Dev"]}
}

class UserProfile:
    def __init__(self, name, current_skills, experience, target_role):
        self.name = name
        self.current_skills = set(s.lower() for s in current_skills)
        self.experience = experience
        self.target_role = target_role

class RecommendationEngine:
    def __init__(self, courses, roles):
        self.courses = courses
        self.roles = roles
    
    def generate_recommendation(self, user):
        required = set(s.lower() for s in self.roles.get(user.target_role, {}).get("required_skills", []))
        missing = required - user.current_skills
        gap_pct = round((len(missing) / len(required)) * 100, 1) if required else 0
        
        matches = []
        for c in self.courses:
            skills = set(s.lower() for s in c["teaches_skills"])
            covered = skills & missing
            if covered:
                matches.append({
                    "course": c,
                    "covered": list(covered),
                    "score": len(covered)
                })
        matches.sort(key=lambda x: x["score"], reverse=True)
        
        rec_courses = []
        for m in matches[:2]:
            rec_courses.append({
                "rank": len(rec_courses)+1,
                "title": m["course"]["title"],
                "url": m["course"]["url"],
                "duration_weeks": m["course"]["duration_weeks"],
                "coverage_percentage": round((m["score"]/len(missing))*100, 1) if missing else 0,
                "skills_covered": m["covered"],
                "why_recommended": f"Covers {m['score']} missing skills: {', '.join(m['covered'])}"
            })
            
        return {
            "user_profile": {"target_role": user.target_role, "current_skill_count": len(user.current_skills)},
            "gap_analysis": {"missing_skills": list(missing), "gap_percentage": gap_pct},
            "recommended_courses": rec_courses,
            "summary": f"Found {len(rec_courses)} courses to bridge your {gap_pct}% skill gap."
        }

# ============================================
# 2. FLASK APP SETUP
# ============================================
app = Flask(__name__)
CORS(app) 
@app.route('/api/recommend', methods=['POST'])
def get_recommendations():
    try:
        data = request.json
        user = UserProfile(
            data.get('name', 'User'),
            data.get('current_skills', []),
            data.get('experience', 0),
            data.get('target_role')
        )
        engine = RecommendationEngine(COURSES, ROLES)
        result = engine.generate_recommendation(user)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
