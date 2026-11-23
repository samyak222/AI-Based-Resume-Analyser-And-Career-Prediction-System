# Pathfinder frontend

React + Vite frontend for the Pathfinder career exploration system.

## Run locally

1. Install dependencies: `npm install`
2. Copy `.env.example` to `.env` and set `VITE_API_URL` if your Flask API is not at `http://127.0.0.1:5000`.
3. Start the frontend: `npm run dev`
4. Build for production: `npm run build`

The questionnaire and profile flow continue to use the existing Flask endpoints:
- `GET /questionnaire`
- `POST /profile`

The CatBoost JSON test panel was removed from the student-facing landing page. Its component remains in `src/MLPredictionPanel.jsx` for developer testing; it is not a resume-upload or personal career prediction feature.
