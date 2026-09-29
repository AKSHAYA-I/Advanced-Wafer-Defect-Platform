from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from app.config import MODEL_DIR, MODEL_VERSION

FEATURES = ['temperature_c','pressure_torr','gas_flow_sccm','etch_rate_nm_min','voltage_v','current_ma','process_step']
NUMERIC = FEATURES[:-1]

class InferenceEngine:
    def __init__(self):
        self.pipeline = joblib.load(MODEL_DIR / 'defect_pipeline.joblib')
        self.detector = joblib.load(MODEL_DIR / 'unknown_detector.joblib')
        self.encoder = joblib.load(MODEL_DIR / 'process_step_encoder.joblib')
        self.threshold = float(joblib.load(MODEL_DIR / 'unknown_threshold.joblib'))
        self.metrics = joblib.load(MODEL_DIR / 'metrics.joblib')

    def validate(self, payload):
        if not np.isfinite([payload[k] for k in NUMERIC]).all():
            raise ValueError('Numeric inputs must be finite.')
        if payload['process_step'] not in list(self.encoder.categories_[0]):
            raise ValueError(f"Unsupported process_step. Supported values: {list(self.encoder.categories_[0])}")

    def frame(self, payload):
        return pd.DataFrame([{k: payload[k] for k in FEATURES}])

    def predict(self, payload):
        self.validate(payload)
        X = self.frame(payload)
        probs = self.pipeline.predict_proba(X)[0]
        idx = int(np.argmax(probs))
        label = str(self.pipeline.classes_[idx])
        confidence = float(probs[idx])
        anomaly_raw = float(self.detector.decision_function(X[NUMERIC])[0])
        anomaly_score = float(np.clip((0.15 - anomaly_raw) / 0.30, 0, 1))
        unknown = anomaly_raw < self.threshold
        return {'predicted_label': label, 'confidence': confidence, 'is_unknown': unknown,
                'status': 'Potential Unknown Defect' if unknown else 'Known Defect',
                'anomaly_score': anomaly_score, 'model_version': MODEL_VERSION,
                'metrics': self.metrics}

engine = None

def get_engine():
    global engine
    if engine is None:
        engine = InferenceEngine()
    return engine
