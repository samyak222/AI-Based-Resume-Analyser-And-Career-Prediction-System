
import joblib
import pandas as pd
from catboost import CatBoostClassifier

# Load model
model = CatBoostClassifier()
model.load_model("binary_stem_catboost.cbm")

# Load metadata
metadata = joblib.load("binary_stem_metadata.joblib")
features = metadata["features"]

print("Tree count:", model.tree_count_)
print("Classes:", model.classes_)
print("Metadata feature count:", len(features))
print("Model feature names count:", len(model.feature_names_))

# Test whether the model accepts 170 named features
test_input = pd.DataFrame(
    [[0.0] * len(features)],
    columns=features
)

try:
    probabilities = model.predict_proba(test_input)
    print("\nSUCCESS: Prediction test passed.")
    print("Probability shape:", probabilities.shape)
    print("Probabilities:", probabilities)
except Exception as e:
    print("\nPrediction test failed:")
    print(type(e).__name__, str(e))
