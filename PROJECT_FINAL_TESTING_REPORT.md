# PROJECT FINAL TESTING REPORT

## AI-Based Resume Analyzer and Career Recommendation System
### Jaypee University of Engineering and Technology, Guna
### B.Tech Minor Project

**Report Generated:** 2026-11-20  
**Testing Environment:** Windows, Python 3.x, Flask 3.1.3, CatBoost 1.2.10, React 19, Vite 8.3.5

---

## 1. Files Inspected

| File | Location | Status |
|------|----------|--------|
| `app.py` | career-backend/ | ✅ Verified |
| `questionnaire.py` | career-backend/ | ✅ Verified |
| `requirements.txt` | career-backend/ | ✅ Verified |
| `check_model.py` | career-backend/ | ✅ Verified |
| `catboost_test_payload.json` | career-backend/ | ✅ Verified |
| `binary_stem_catboost.cbm` | career-backend/ | ✅ Model loads correctly |
| `binary_stem_metadata.joblib` | career-backend/ | ✅ Metadata loads correctly |
| `App.jsx` | career-frontend/src/ | ✅ Verified |
| `MLPredictionPanel.jsx` | career-frontend/src/ | ✅ Verified |
| `main.jsx` | career-frontend/src/ | ✅ Verified |
| `App.css` | career-frontend/src/ | ✅ Verified (2063 lines) |
| `index.css` | career-frontend/src/ | ✅ Verified |
| `package.json` | career-frontend/ | ✅ Verified |
| `vite.config.js` | career-frontend/ | ✅ Verified |
| `index.html` | career-frontend/ | ✅ Modified |
| `eslint.config.js` | career-frontend/ | ✅ Verified |

---

## 2. Files Modified

| File | Change | Reason |
|------|--------|--------|
| `career-frontend/index.html` | Updated `<title>` and added `<meta description>` | Generic "career-frontend" title replaced with "Pathfinder – AI Career Recommendation System" for proper SEO and demo presentation |

---

## 3. Bugs Identified and Fixed

| # | Issue | Severity | Fix Applied |
|---|-------|----------|-------------|
| 1 | PowerShell execution policy blocked `npm` commands | Medium | Set `RemoteSigned` execution policy for CurrentUser |
| 2 | Generic HTML title "career-frontend" | Low | Updated to descriptive project title |

**No critical bugs found.** The existing codebase was well-implemented with proper error handling, CORS configuration, model loading, and input validation.

---

## 4. Backend API Testing Results

### CatBoost Model Verification

| Check | Result |
|-------|--------|
| Model file found | ✅ binary_stem_catboost.cbm |
| Metadata file found | ✅ binary_stem_metadata.joblib |
| Feature count | 170 |
| Tree count | 136 |
| Model classes | [0, 1] (binary: Non-STEM / STEM) |
| Feature order match | ✅ Metadata matches model |
| Prediction test | ✅ Probabilities: [0.598, 0.402] |

### API Endpoint Tests

| # | Test Case | Method | Endpoint | Expected | Actual | Status |
|---|-----------|--------|----------|----------|--------|--------|
| 1 | Home page | GET | `/` | 200 + welcome message | `{"message": "PATHFINDER Career Recommendation API is running", "status": "ok"}` | ✅ PASS |
| 2 | Health check | GET | `/health` | 200 + model info | `{"status": "healthy", "model_loaded": true, "feature_count": 170, "tree_count": 136}` | ✅ PASS |
| 3 | Get features | GET | `/features` | 200 + 170 features | Feature count: 170, features listed correctly | ✅ PASS |
| 4 | Get questionnaire | GET | `/questionnaire` | 200 + 30 questions | Title: "Career Exploration Questionnaire", total: 30, 3 sections | ✅ PASS |
| 5 | Valid prediction | POST | `/predict` | 200 + STEM/Non-STEM | `{"predicted_label": "Non-STEM", "prediction": 0, "stem_probability": 0.3578}` | ✅ PASS |
| 6 | Valid profile | POST | `/profile` | 200 + recommendations | 3 career recommendations with match scores, skills, roadmaps | ✅ PASS |
| 7 | Incomplete answers | POST | `/profile` | 400 + missing list | `{"error": "Some answers are missing.", "missing_count": 28}` | ✅ PASS |
| 8 | Empty body | POST | `/profile` | 400 + error message | `{"error": "An 'answers' object is required."}` | ✅ PASS |
| 9 | Invalid answers | POST | `/profile` | 400 + invalid list | `{"error": "Each answer must be one of a, b, c, or d.", "invalid_questions": ["q1"]}` | ✅ PASS |
| 10 | Malformed JSON | POST | `/profile` | 400 + error | `{"error": "Send a JSON object."}` | ✅ PASS |
| 11 | Missing features (predict) | POST | `/predict` | 400 + missing info | `{"error": "Required model features are missing.", "missing_count": 169}` | ✅ PASS |
| 12 | Empty predict body | POST | `/predict` | 400 + error | `{"error": "Provide a 'features' object containing model inputs."}` | ✅ PASS |
| 13 | Repeated valid requests | POST | `/predict` | 200 consistent | Both returned "Non-STEM" with same probability | ✅ PASS |

**All 13 API tests PASSED.**

---

## 5. CatBoost API Testing Results

| Test | Expected | Actual | Status |
|------|----------|--------|--------|
| Model loads at startup | Model loaded message | "CatBoost model loaded successfully! Feature count: 170, Tree count: 136" | ✅ PASS |
| Feature names match metadata | Names match | Model and metadata features are identical | ✅ PASS |
| Binary classification | Classes [0, 1] | Confirmed binary model | ✅ PASS |
| Prediction with test payload | Valid prediction | Non-STEM (probability 0.3578) | ✅ PASS |
| Null/NaN handling | Treated as missing | Model accepts NaN values | ✅ PASS |
| Boolean rejection | 400 error | Properly rejected | ✅ PASS |

---

## 6. Frontend-Backend Integration Status

| Component | Status | Details |
|-----------|--------|---------|
| Frontend builds | ✅ | 18 modules transformed, no errors |
| Frontend dev server | ✅ | Running at http://localhost:5173/ |
| Backend server | ✅ | Running at http://127.0.0.1:5000 |
| CORS configuration | ✅ | `flask-cors` enabled on all routes |
| API URL in frontend | ✅ | Correctly set to `http://127.0.0.1:5000` |
| Questionnaire fetch | ✅ | Frontend fetches 30 questions from `/questionnaire` |
| Answer submission | ✅ | Frontend POSTs to `/profile` with correct format |
| Results display | ✅ | Career recommendations, match scores, roadmaps rendered |
| ML prediction panel | ✅ | File upload → CatBoost prediction working |
| Error handling | ✅ | Connection errors, validation errors handled gracefully |
| Loading states | ✅ | Spinner and disabled buttons during loading |

---

## 7. End-to-End Workflow Status

### Questionnaire Workflow
1. ✅ Student opens http://localhost:5173/
2. ✅ Application loads with hero section and questionnaire
3. ✅ 30 questions fetched from Flask backend
4. ✅ Student answers questions one-by-one with navigation
5. ✅ Progress bar updates in real-time
6. ✅ Frontend submits all 30 answers to `/profile`
7. ✅ Results display: career recommendations, match scores, learning roadmaps
8. ✅ Career comparison feature (up to 3 careers)
9. ✅ Restart questionnaire functionality

### ML Prediction Workflow
1. ✅ ML prediction panel visible on main page
2. ✅ User uploads JSON test payload file
3. ✅ Frontend sends payload to `/predict`
4. ✅ STEM/Non-STEM prediction displayed with probability bar

---

## 8. Remaining Incomplete Features

| Feature | Status | Notes |
|---------|--------|-------|
| Resume Upload & Parsing | ❌ Not implemented | No PDF/DOCX upload, text extraction, or skill parsing exists. Documented as **future scope**. |
| Resume-to-Job Matching | ❌ Not implemented | Requires resume parsing first. Documented as **future scope**. |
| User Authentication | ❌ Not implemented | Not required for demonstration |
| Database Storage | ❌ Not implemented | Results are session-only |
| Deployment | ❌ Not configured | Running as development servers |

### Future Scope: Resume Analyzer
The official project title includes "Resume Analyzer." The current implementation focuses on:
- **Educational-data-based career prediction** (CatBoost ML model on HSLS:09 dataset)
- **Questionnaire-based student career profiling** (30-question assessment)

A resume analysis module would include:
- PDF/DOCX file upload and text extraction
- Skill keyword extraction using NLP
- Resume-to-career matching based on extracted skills
- Integration with the existing career recommendation engine

---

## 9. Commands to Run the Backend

```powershell
# Navigate to backend directory and start Flask
cd C:\Users\victus\Desktop\Ai-Based-Career-Recommendation-System\career-backend
python app.py
```

Expected output:
```
CatBoost model loaded successfully!
Feature count: 170
Tree count: 136
 * Serving Flask app 'app'
 * Running on http://127.0.0.1:5000
```

---

## 10. Commands to Run the Frontend

```powershell
# Navigate to frontend directory and start Vite dev server
cd C:\Users\victus\Desktop\Ai-Based-Career-Recommendation-System\career-frontend
npm run dev
```

Expected output:
```
  VITE v8.3.5  ready in 602 ms
  ➜  Local:   http://localhost:5173/
```

**Note:** If you encounter a PowerShell execution policy error, run this first:
```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned -Force
```

---

## 11. Browser URL for Working Application

| Component | URL |
|-----------|-----|
| **Frontend** | http://localhost:5173/ |
| **Backend API** | http://127.0.0.1:5000 |
| **Health Check** | http://127.0.0.1:5000/health |

---

## 12. Postman Requests for Demonstration

See `POSTMAN_DEMO.md` in the project root for complete cURL/PowerShell commands.

### Quick Demo Commands:

```powershell
# 1. Health check
Invoke-RestMethod -Uri 'http://127.0.0.1:5000/health'

# 2. Get questionnaire
Invoke-RestMethod -Uri 'http://127.0.0.1:5000/questionnaire'

# 3. CatBoost prediction
$payload = Get-Content 'career-backend\catboost_test_payload.json' -Raw
Invoke-RestMethod -Uri 'http://127.0.0.1:5000/predict' -Method Post -ContentType 'application/json' -Body $payload

# 4. Submit questionnaire answers
$body = '{"answers":{"q1":"a","q2":"b","q3":"c","q4":"d","q5":"a","q6":"b","q7":"c","q8":"d","q9":"a","q10":"b","q11":"c","q12":"c","q13":"a","q14":"d","q15":"c","q16":"c","q17":"b","q18":"a","q19":"c","q20":"c","q21":"a","q22":"b","q23":"c","q24":"d","q25":"a","q26":"b","q27":"c","q28":"d","q29":"a","q30":"b"}}'
Invoke-RestMethod -Uri 'http://127.0.0.1:5000/profile' -Method Post -ContentType 'application/json' -Body $body
```

---

## 13. Project Completion Summary

### Architecture

```
┌─────────────────────────────────────────┐
│          React + Vite Frontend          │
│          http://localhost:5173          │
│                                         │
│  ┌─────────────┐  ┌──────────────────┐ │
│  │ Questionnaire│  │ ML Prediction    │ │
│  │ (30 Q&A)    │  │ Panel (CatBoost) │ │
│  └──────┬──────┘  └───────┬──────────┘ │
└─────────┼─────────────────┼────────────┘
          │ REST API        │ REST API
┌─────────┼─────────────────┼────────────┐
│         ▼                 ▼            │
│    Flask Backend (Port 5000)           │
│                                        │
│  ┌────────────────┐ ┌───────────────┐  │
│  │ questionnaire.py│ │ app.py        │  │
│  │ GET /questionnaire│ │ GET /health │  │
│  │ POST /profile  │ │ GET /features │  │
│  └────────────────┘ │ POST /predict │  │
│                     └───────────────┘  │
│                           │            │
│                     ┌─────▼─────────┐  │
│                     │ CatBoost Model│  │
│                     │ 170 features  │  │
│                     │ 136 trees     │  │
│                     │ Binary STEM   │  │
│                     └───────────────┘  │
└────────────────────────────────────────┘
```

### ML Model Details

| Metric | Value |
|--------|-------|
| Algorithm | CatBoost Classifier |
| Dataset | HSLS:09 (High School Longitudinal Study 2009) |
| Target | Binary STEM vs Non-STEM |
| Features | 170 (Wave-1 variables) |
| Trees | 136 |
| Reported ROC-AUC | 0.7248 |
| Reported Macro-F1 | 0.6114 |
| Class distribution | ~16.6% STEM, ~83.4% Non-STEM |

### Questionnaire Module

| Component | Details |
|-----------|---------|
| Total questions | 30 |
| Personal interests (Q1-Q10) | 10 questions measuring preferences |
| Logical reasoning (Q11-Q20) | 10 questions with correct answers |
| Scenario-based (Q21-Q30) | 10 real-life situation questions |
| Recommendation engine | Heuristic scoring (65% personal + 35% scenario) |
| Output | Top 3 career recommendations with match scores, skills, projects, 4-week roadmaps |

### Demonstration Sequence

1. Start Flask backend: `python app.py` (from career-backend/)
2. Start React frontend: `npm run dev` (from career-frontend/)
3. Open http://localhost:5173/ in browser
4. Show the hero page with career exploration intro
5. Answer all 30 questions (personal interests → logical reasoning → scenarios)
6. View career recommendations with match scores
7. Compare up to 3 careers side-by-side
8. Show skills, beginner projects, and 4-week learning roadmaps
9. Upload `catboost_test_payload.json` in the ML prediction panel
10. Show STEM/Non-STEM prediction with probability score
11. (Fallback) Use PowerShell/Postman commands from POSTMAN_DEMO.md

---

**Report Status:** All verified implementation and testing results confirmed through actual execution.
