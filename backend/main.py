from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db.database import Base, engine, SessionLocal
from app.db.models import ModelVersion
from app.routers.core import router
from app.config import MODEL_DIR, MODEL_VERSION
from pathlib import Path

Base.metadata.create_all(bind=engine)
app=FastAPI(title='Advanced Wafer Defect Intelligence Platform',version=MODEL_VERSION)
app.add_middleware(CORSMiddleware,allow_origins=[
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "YOUR-FRONTEND-URL",
],allow_credentials=True,allow_methods=['*'],allow_headers=['*'])
app.include_router(router)

@app.get('/')
def root(): return {'message':'Semiconductor Wafer Intelligence API','docs':'/docs'}

@app.on_event('startup')
def startup():
    required=['defect_pipeline.joblib','unknown_detector.joblib','process_step_encoder.joblib','unknown_threshold.joblib','metrics.joblib']
    if not all((MODEL_DIR/x).exists() for x in required):
        from app.models.training import train
        train()
    db=SessionLocal()
    try:
        if not db.query(ModelVersion).filter_by(version=MODEL_VERSION).first():
            import joblib
            m=joblib.load(MODEL_DIR/'metrics.joblib')
            db.add(ModelVersion(model_name='defect+unknown',version=MODEL_VERSION,accuracy=m['accuracy'],precision=m['precision'],recall=m['recall'],macro_f1=m['macro_f1'],unknown_detection_f1=0.0,dataset_version=m.get('dataset_source','unknown'),status='production',path=str(MODEL_DIR))); db.commit()
    finally: db.close()
