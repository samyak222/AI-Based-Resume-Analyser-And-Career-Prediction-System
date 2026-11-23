
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from catboost import CatBoostClassifier
from flask import Flask, jsonify, request
from flask_cors import CORS

from questionnaire import questionnaire_bp


# --------------------------------------------------
# 1. Flask application setup
# --------------------------------------------------

app = Flask(__name__)
CORS(app)

# Register questionnaire endpoints
app.register_blueprint(questionnaire_bp)


# --------------------------------------------------
# 2. Load trained CatBoost model and metadata
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent

MODEL_PATH = BASE_DIR / "binary_stem_catboost.cbm"
METADATA_PATH = BASE_DIR / "binary_stem_metadata.joblib"

if not MODEL_PATH.is_file():
    raise FileNotFoundError(
        f"CatBoost model file not found: {MODEL_PATH}"
    )

if not METADATA_PATH.is_file():
    raise FileNotFoundError(
        f"Model metadata file not found: {METADATA_PATH}"
    )

model = CatBoostClassifier()
model.load_model(str(MODEL_PATH))

metadata = joblib.load(METADATA_PATH)
FEATURES = metadata["features"]

# Validate feature names and their order.
if FEATURES != model.feature_names_:
    raise RuntimeError(
        "Model and metadata feature names/order do not match."
    )

if list(model.classes_) != [0, 1]:
    raise RuntimeError(
        "Expected a binary CatBoost model with classes [0, 1]."
    )

print("CatBoost model loaded successfully!")
print("Feature count:", len(FEATURES))
print("Tree count:", model.tree_count_)


# --------------------------------------------------
# 3. Home endpoint
# --------------------------------------------------

@app.get("/")
def home():
    return jsonify({
        "message": "PATHFINDER Career Recommendation API is running",
        "status": "ok"
    })


# --------------------------------------------------
# 4. Health check endpoint
# --------------------------------------------------

@app.get("/health")
def health():
    return jsonify({
        "status": "healthy",
        "model_loaded": True,
        "feature_count": len(FEATURES),
        "tree_count": model.tree_count_
    })


# --------------------------------------------------
# 5. Get model feature names
# --------------------------------------------------

@app.get("/features")
def get_features():
    return jsonify({
        "feature_count": len(FEATURES),
        "features": FEATURES
    })


# --------------------------------------------------
# 6. CatBoost STEM prediction endpoint
# --------------------------------------------------

@app.post("/predict")
def predict():
    body = request.get_json(silent=True)

    if not isinstance(body, dict):
        return jsonify({
            "error": "Request must contain a valid JSON object."
        }), 400

    features = body.get("features")

    if not isinstance(features, dict):
        return jsonify({
            "error": "Provide a 'features' object containing model inputs."
        }), 400

    # Check that all required features are provided.
    missing = [
        name for name in FEATURES
        if name not in features
    ]

    if missing:
        return jsonify({
            "error": "Required model features are missing.",
            "missing_count": len(missing),
            "missing_features": missing
        }), 400

    # Build a row in the exact feature order expected by the model.
    row = {}

    for name in FEATURES:
        value = features[name]

        # Missing values are represented as NaN.
        if value is None:
            row[name] = np.nan
            continue

        # Reject booleans even though Python treats them as integers.
        if isinstance(value, bool):
            return jsonify({
                "error": f"Boolean value is not allowed for '{name}'."
            }), 400

        try:
            number = float(value)
        except (TypeError, ValueError, OverflowError):
            return jsonify({
                "error": f"Feature '{name}' must be numeric or null."
            }), 400

        # NaN is treated as a missing value; infinity is rejected.
        if np.isnan(number):
            row[name] = np.nan
            continue

        if not np.isfinite(number):
            return jsonify({
                "error": f"Feature '{name}' cannot be infinite."
            }), 400

        row[name] = number

    try:
        input_df = pd.DataFrame(
            [row],
            columns=FEATURES
        )

        # Get probabilities for both classes.
        probabilities = model.predict_proba(input_df)[0]
        classes = list(model.classes_)

        stem_probability = float(
            probabilities[classes.index(1)]
        )

        predicted_class = int(
            np.asarray(model.predict(input_df)).reshape(-1)[0]
        )

        return jsonify({
            "prediction": predicted_class,
            "predicted_label": (
                "STEM" if predicted_class == 1 else "Non-STEM"
            ),
            "stem_probability": round(stem_probability, 4),
            "note": (
                "This estimates alignment with the model's "
                "self-reported STEM aspiration target. It does not "
                "determine a student's actual future career."
            )
        }), 200

    except Exception:
        app.logger.exception("CatBoost prediction failed")

        return jsonify({
            "error": "Prediction failed due to an internal error."
        }), 500


# --------------------------------------------------
# 7. Start the Flask development server
# --------------------------------------------------

if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False
    )
