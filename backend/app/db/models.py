from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
from datetime import datetime, timezone
from app.db.database import Base

class Prediction(Base):
    __tablename__ = 'predictions'
    id = Column(Integer, primary_key=True)
    sample_id = Column(String, index=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    predicted_label = Column(String)
    confidence = Column(Float)
    is_unknown = Column(Boolean, default=False)
    anomaly_score = Column(Float)
    model_version = Column(String)

class RootCauseResult(Base):
    __tablename__ = 'root_cause_results'
    id = Column(Integer, primary_key=True)
    prediction_id = Column(Integer, ForeignKey('predictions.id'))
    process_step = Column(String)
    parameter = Column(String)
    probability = Column(Float)
    explanation = Column(Text)

class EngineerFeedback(Base):
    __tablename__ = 'engineer_feedback'
    id = Column(Integer, primary_key=True)
    prediction_id = Column(Integer, ForeignKey('predictions.id'))
    predicted_label = Column(String)
    actual_label = Column(String)
    confirmed_root_cause = Column(String)
    prediction_correct = Column(Boolean)
    status = Column(String, default='PENDING')
    engineer_comment = Column(Text)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class ModelVersion(Base):
    __tablename__ = 'model_versions'
    id = Column(Integer, primary_key=True)
    model_name = Column(String)
    version = Column(String, unique=True)
    accuracy = Column(Float)
    precision = Column(Float)
    recall = Column(Float)
    macro_f1 = Column(Float)
    unknown_detection_f1 = Column(Float)
    training_date = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    dataset_version = Column(String)
    status = Column(String, default='candidate')
    path = Column(String)
