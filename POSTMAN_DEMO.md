# Postman / cURL API Demonstration Guide

> **Backend URL:** `http://127.0.0.1:5000`
> Start the backend first: `cd career-backend && python app.py`

---

## 1. Health Check

**GET** `http://127.0.0.1:5000/health`

```powershell
Invoke-RestMethod -Uri 'http://127.0.0.1:5000/health'
```

Expected: `{ "status": "healthy", "model_loaded": true, "feature_count": 170, ... }`

---

## 2. Get Model Features

**GET** `http://127.0.0.1:5000/features`

```powershell
Invoke-RestMethod -Uri 'http://127.0.0.1:5000/features'
```

Expected: `{ "feature_count": 170, "features": [...] }`

---

## 3. CatBoost STEM Prediction

**POST** `http://127.0.0.1:5000/predict`

```powershell
$payload = Get-Content 'career-backend\catboost_test_payload.json' -Raw
Invoke-RestMethod -Uri 'http://127.0.0.1:5000/predict' -Method Post -ContentType 'application/json' -Body $payload
```

Expected: `{ "prediction": 0 or 1, "predicted_label": "STEM" or "Non-STEM", "stem_probability": 0.xxxx }`

---

## 4. Get Questionnaire Questions

**GET** `http://127.0.0.1:5000/questionnaire`

```powershell
Invoke-RestMethod -Uri 'http://127.0.0.1:5000/questionnaire'
```

Expected: `{ "title": "Career Exploration Questionnaire", "total_questions": 30, "questions": [...] }`

---

## 5. Submit Complete Questionnaire Answers

**POST** `http://127.0.0.1:5000/profile`

```powershell
$body = '{"answers":{"q1":"a","q2":"b","q3":"c","q4":"d","q5":"a","q6":"b","q7":"c","q8":"d","q9":"a","q10":"b","q11":"c","q12":"c","q13":"a","q14":"d","q15":"c","q16":"c","q17":"b","q18":"a","q19":"c","q20":"c","q21":"a","q22":"b","q23":"c","q24":"d","q25":"a","q26":"b","q27":"c","q28":"d","q29":"a","q30":"b"}}'
Invoke-RestMethod -Uri 'http://127.0.0.1:5000/profile' -Method Post -ContentType 'application/json' -Body $body
```

Expected: Full career profile with recommendations, logical reasoning score, interest counts, and learning roadmaps.

---

## 6. Error Handling — Incomplete Answers

**POST** `http://127.0.0.1:5000/profile`

```powershell
$body = '{"answers":{"q1":"a","q2":"b"}}'
Invoke-RestMethod -Uri 'http://127.0.0.1:5000/profile' -Method Post -ContentType 'application/json' -Body $body
```

Expected: 400 error with `missing_questions` list.

---

## 7. Error Handling — Empty Body

**POST** `http://127.0.0.1:5000/profile`

```powershell
Invoke-RestMethod -Uri 'http://127.0.0.1:5000/profile' -Method Post -ContentType 'application/json' -Body '{}'
```

Expected: 400 error: "An 'answers' object is required."

---

## 8. Error Handling — Invalid Answers

**POST** `http://127.0.0.1:5000/profile`

```powershell
$body = '{"answers":{"q1":"z","q2":"b","q3":"c","q4":"d","q5":"a","q6":"b","q7":"c","q8":"d","q9":"a","q10":"b","q11":"c","q12":"c","q13":"a","q14":"d","q15":"c","q16":"c","q17":"b","q18":"a","q19":"c","q20":"c","q21":"a","q22":"b","q23":"c","q24":"d","q25":"a","q26":"b","q27":"c","q28":"d","q29":"a","q30":"b"}}'
Invoke-RestMethod -Uri 'http://127.0.0.1:5000/profile' -Method Post -ContentType 'application/json' -Body $body
```

Expected: 400 error: "Each answer must be one of a, b, c, or d." with `invalid_questions: ["q1"]`
