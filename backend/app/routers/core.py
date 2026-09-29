from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import Prediction, RootCauseResult, EngineerFeedback, ModelVersion
from app.models.inference import get_engine
from app.models.root_cause import rank_causes
from app.schemas import WaferInput, PredictionRequest, WhatIfRequest, FeedbackRequest, RetrainRequest
from app.config import MODEL_VERSION, MODEL_DIR
import uuid, copy

router=APIRouter()

def health_payload():
    out={'api':True,'database':True,'preprocessor':False,'defect_model':False,'unknown_detector':False,'cause_model':True}
    try:
        e=get_engine(); out.update(preprocessor=True,defect_model=True,unknown_detector=True)
    except Exception: pass
    out['status']='healthy' if all(out.values()) else 'degraded'
    return out

@router.get('/health')
def health(): return health_payload()

@router.post('/preprocess')
def preprocess(payload: WaferInput):
    try:
        e=get_engine(); e.validate(payload.model_dump())
        # Use the saved inference pipeline's transformer without fitting anything.
        X=e.frame(payload.model_dump()); Xt=e.pipeline.named_steps['prep'].transform(X)
        return {'valid':True,'original':payload.model_dump(),'transformed_feature_count':int(Xt.shape[1]),'process_step':payload.process_step}
    except ValueError as ex: raise HTTPException(422,str(ex))
    except Exception as ex: raise HTTPException(503,'Preprocessing artifacts are unavailable.')

@router.post('/predict')
def predict(payload: PredictionRequest, db: Session=Depends(get_db)):
    try: result=get_engine().predict(payload.model_dump())
    except ValueError as ex: raise HTTPException(422,str(ex))
    except Exception: raise HTTPException(503,'Prediction model is unavailable.')
    p=Prediction(sample_id=payload.sample_id or str(uuid.uuid4()),predicted_label=result['predicted_label'],confidence=result['confidence'],is_unknown=result['is_unknown'],anomaly_score=result['anomaly_score'],model_version=MODEL_VERSION)
    db.add(p); db.commit(); db.refresh(p); result['prediction_id']=p.id
    return result

@router.post('/unknown-defect')
def unknown_defect(payload: PredictionRequest):
    try: r=get_engine().predict(payload.model_dump())
    except ValueError as ex: raise HTTPException(422,str(ex))
    except Exception: raise HTTPException(503,'Unknown detector is unavailable.')
    return {k:r[k] for k in ['is_unknown','status','anomaly_score','confidence','model_version']}

@router.post('/recommend-cause')
def recommend_cause(payload: WaferInput):
    try: get_engine().validate(payload.model_dump())
    except ValueError as ex: raise HTTPException(422,str(ex))
    return {'results':rank_causes(payload.model_dump()),'disclaimer':'Probable, model-based decision support; not proof of physical causation.'}

@router.post('/what-if')
def what_if(payload: WhatIfRequest):
    base=payload.model_dump(); mod=copy.deepcopy(base); name=payload.modified_parameter
    if name not in ['temperature_c','pressure_torr','gas_flow_sccm','etch_rate_nm_min','voltage_v','current_ma']:
        raise HTTPException(422,'modified_parameter must be a numeric process parameter.')
    mod[name]=payload.modified_value
    try:
        a=get_engine().predict(base); b=get_engine().predict(mod)
    except ValueError as ex: raise HTTPException(422,str(ex))
    return {'baseline_probability':a['confidence'],'counterfactual_probability':b['confidence'],'difference':b['confidence']-a['confidence'],
            'modified_parameter':name,'modified_value':payload.modified_value,'model_version':MODEL_VERSION,
            'disclaimer':'Model-based scenario analysis; not a guarantee of physical process outcome.'}

@router.post('/feedback')
def feedback(payload: FeedbackRequest, db: Session=Depends(get_db)):
    p=db.get(Prediction,payload.prediction_id)
    if not p: raise HTTPException(404,'Prediction not found.')
    f=EngineerFeedback(prediction_id=p.id,predicted_label=p.predicted_label,actual_label=payload.actual_label,confirmed_root_cause=payload.confirmed_root_cause,prediction_correct=payload.prediction_correct,engineer_comment=payload.engineer_comment,status='PENDING')
    db.add(f); db.commit(); db.refresh(f); return {'id':f.id,'status':f.status}

@router.get('/feedback')
def list_feedback(db: Session=Depends(get_db)):
    return [{'id':f.id,'prediction_id':f.prediction_id,'predicted_label':f.predicted_label,'actual_label':f.actual_label,'status':f.status,'comment':f.engineer_comment} for f in db.query(EngineerFeedback).order_by(EngineerFeedback.id.desc()).all()]

@router.post('/feedback/{feedback_id}/validate')
def validate_feedback(feedback_id:int, db:Session=Depends(get_db)):
    f=db.get(EngineerFeedback,feedback_id)
    if not f: raise HTTPException(404,'Feedback not found.')
    f.status='VALIDATED'; db.commit(); return {'id':f.id,'status':f.status}

@router.get('/models')
def models(db:Session=Depends(get_db)):
    return [{'version':m.version,'model_name':m.model_name,'accuracy':m.accuracy,'precision':m.precision,'recall':m.recall,'macro_f1':m.macro_f1,'status':m.status,'dataset_version':m.dataset_version} for m in db.query(ModelVersion).order_by(ModelVersion.id.desc()).all()]

@router.get('/mlops')
def mlops(db:Session=Depends(get_db)):
    e=get_engine(); return {'current_model':MODEL_VERSION,'metrics':e.metrics,'drift_status':'NOT_CONFIGURED','last_training':'See model registry','note':'Drift monitoring requires production reference/current batches; no fabricated drift result is shown.'}

@router.post('/mlops/retrain')
def retrain(payload:RetrainRequest):
    if not payload.confirm: raise HTTPException(400,'Set confirm=true to start controlled retraining.')
    from app.models.training import train
    metrics=train(); return {'status':'candidate_trained','metrics':metrics,'promotion':'not automatic'}

@router.get('/dashboard')
def dashboard(db:Session=Depends(get_db)):
    total=db.query(Prediction).count(); unknown=db.query(Prediction).filter(Prediction.is_unknown==True).count()
    return {'total_samples_analyzed':total,'potential_unknown_defects':unknown,'model_version':MODEL_VERSION,'metrics':get_engine().metrics}
