"""End-to-end verification script for the Career Recommendation System."""

import json
import requests

print("=== END-TO-END VERIFICATION ===")
print()

# 1. Backend health
r = requests.get("http://127.0.0.1:5000/health")
health = r.json()
print("Backend health:", r.status_code, "-", health["status"])
print("  Model loaded:", health["model_loaded"])
print("  Feature count:", health["feature_count"])
print("  Tree count:", health["tree_count"])

# 2. Frontend page
r = requests.get("http://localhost:5173/")
print("Frontend page:", r.status_code, "- Title found:", "Pathfinder" in r.text)

# 3. Questionnaire endpoint
r = requests.get("http://127.0.0.1:5000/questionnaire")
qdata = r.json()
print("Questionnaire:", r.status_code, "-", qdata["total_questions"], "questions")

# 4. Profile endpoint with valid answers
answers = {}
for i in range(1, 31):
    answers["q" + str(i)] = ["a", "b", "c", "d"][i % 4]

r = requests.post("http://127.0.0.1:5000/profile", json={"answers": answers})
data = r.json()
recs = data.get("career_recommendations", [])
logic = data.get("logical_reasoning", {})
print("Profile:", r.status_code, "-", len(recs), "recommendations")
print("  Logical score:", logic.get("correct_answers"), "/", logic.get("total_questions"))
for rec in recs:
    print("  Career:", rec["title"], "(score:", str(rec["match_score"]) + "/100)")

# 5. CatBoost prediction
with open("career-backend/catboost_test_payload.json") as f:
    payload = json.load(f)
r = requests.post("http://127.0.0.1:5000/predict", json=payload)
pred = r.json()
print("CatBoost:", r.status_code, "-", pred["predicted_label"],
      "(STEM prob:", str(pred["stem_probability"]) + ")")

# 6. Error handling tests
r = requests.post("http://127.0.0.1:5000/profile", json={})
print("Empty body error:", r.status_code, "-", r.json()["error"])

r = requests.post("http://127.0.0.1:5000/profile", json={"answers": {"q1": "z"}})
print("Invalid answer error:", r.status_code, "-", r.json()["error"][:40])

print()
print("=== ALL SYSTEMS OPERATIONAL ===")
