import { useState } from "react";
import "./App.css";

const API_URL = "http://127.0.0.1:5000";

export default function MLPredictionPanel() {
  const [file, setFile] = useState(null);
  const [prediction, setPrediction] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handlePredict() {
    if (!file) {
      setError("Please select your CatBoost test JSON file first.");
      return;
    }

    setLoading(true);
    setError("");
    setPrediction(null);

    try {
      const payload = JSON.parse(await file.text());

      if (
        !payload.features ||
        typeof payload.features !== "object" ||
        Array.isArray(payload.features)
      ) {
        throw new Error('Invalid JSON format. Expected {"features": {...}}.');
      }

      const response = await fetch(`${API_URL}/predict`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.error || "Prediction request failed.");
      }

      setPrediction(data);
    } catch (err) {
      setError(
        err.message ||
          "Could not connect to Flask. Check that the backend is running."
      );
    } finally {
      setLoading(false);
    }
  }

  const probability = prediction
    ? Math.max(0, Math.min(100, Number(prediction.stem_probability) * 100))
    : 0;

  return (
    <section className="ml-test-panel" aria-labelledby="ml-panel-title">
      <div className="ml-panel-heading">
        <p className="eyebrow">MACHINE LEARNING · INTEGRATION TEST</p>
        <h2 id="ml-panel-title">CatBoost STEM prediction</h2>
        <p>
          Upload the existing 170-feature test payload to verify that the React
          frontend can communicate with the ML API.
        </p>
      </div>

      <div className="ml-upload-area">
        <label htmlFor="ml-test-file">Test payload (.json)</label>
        <input
          id="ml-test-file"
          type="file"
          accept=".json,application/json"
          onChange={(event) => {
            setFile(event.target.files?.[0] || null);
            setPrediction(null);
            setError("");
          }}
        />
        <button
          type="button"
          className="primary-button"
          onClick={handlePredict}
          disabled={loading || !file}
        >
          {loading ? "Running prediction..." : "Run CatBoost prediction"}
          {!loading && <span>→</span>}
        </button>
      </div>

      {error && <p className="ml-error" role="alert">{error}</p>}

      {prediction && (
        <div className="ml-prediction-result" aria-live="polite">
          <p className="eyebrow">MODEL RESPONSE</p>
          <h3>{prediction.predicted_label}</h3>
          <div className="ml-probability-row">
            <span>Estimated STEM probability</span>
            <strong>{probability.toFixed(2)}%</strong>
          </div>
          <div
            className="ml-probability-track"
            role="progressbar"
            aria-label="Estimated STEM probability"
            aria-valuemin={0}
            aria-valuemax={100}
            aria-valuenow={probability}
          >
            <div className="ml-probability-fill" style={{ width: `${probability}%` }} />
          </div>
          <p className="ml-note">{prediction.note}</p>
        </div>
      )}

      <p className="ml-disclaimer">
        Developer test only. This uses an existing dataset test sample, not
        answers from the career questionnaire. It is not a personal career
        assessment.
      </p>
    </section>
  );
}
