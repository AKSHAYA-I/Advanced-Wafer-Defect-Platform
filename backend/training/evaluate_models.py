import joblib
from app.config import MODEL_DIR
print(joblib.load(MODEL_DIR/'metrics.joblib'))
