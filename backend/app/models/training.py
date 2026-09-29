from pathlib import Path
import numpy as np, pandas as pd, joblib
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.preprocessing import OneHotEncoder
from app.config import DATASET_PATH, MODEL_DIR
from app.models.inference import FEATURES, NUMERIC

CLASSES=['Normal','Particle','Pattern','Metal']
STEPS=['CMP','Deposition','Etching','Lithography','Oxidation']

def make_demo_dataset(path=DATASET_PATH, n=1600):
    rng=np.random.default_rng(42)
    steps=rng.choice(STEPS,n)
    temp=rng.normal(450,28,n); pressure=rng.normal(35,6,n); gas=rng.normal(150,28,n)
    etch=rng.normal(80,12,n); voltage=rng.normal(220,22,n); current=rng.normal(15,3,n)
    score=(temp>475).astype(int)+(pressure<27).astype(int)+(gas>190).astype(int)+(etch<65).astype(int)
    labels=np.array(CLASSES)[np.minimum(score,3)]
    # Add noise so classes are not deterministically defined.
    flip=rng.random(n)<0.12
    labels[flip]=rng.choice(CLASSES,flip.sum())
    df=pd.DataFrame({'temperature_c':temp,'pressure_torr':pressure,'gas_flow_sccm':gas,'etch_rate_nm_min':etch,
                     'voltage_v':voltage,'current_ma':current,'process_step':steps,'defect_label':labels})
    df.to_csv(path,index=False); return df

def train(path=DATASET_PATH):
    generated = not path.exists()
    if generated:
        df=make_demo_dataset(path)
    else: df=pd.read_csv(path)
    required=FEATURES+['defect_label']
    missing=[c for c in required if c not in df.columns]
    if missing: raise ValueError(f'Missing required columns: {missing}')
    df=df.dropna(subset=required).copy()
    X=df[FEATURES]; y=df['defect_label'].astype(str)
    Xtr,Xte,ytr,yte=train_test_split(X,y,test_size=.2,random_state=42,stratify=y)
    prep=ColumnTransformer([('num',StandardScaler(),NUMERIC),('cat',OneHotEncoder(handle_unknown='ignore'),['process_step'])])
    pipe=Pipeline([('prep',prep),('model',RandomForestClassifier(n_estimators=250,class_weight='balanced',random_state=42,n_jobs=-1))])
    pipe.fit(Xtr,ytr); pred=pipe.predict(Xte)
    metrics={'accuracy':accuracy_score(yte,pred),'precision':precision_score(yte,pred,average='macro',zero_division=0),
             'recall':recall_score(yte,pred,average='macro',zero_division=0),'macro_f1':f1_score(yte,pred,average='macro',zero_division=0),
             'dataset_rows':len(df),'dataset_source':'demo-generated' if generated else 'provided'}
    # detector on raw numeric process features; thresholds are calibrated from validation distribution.
    det=IsolationForest(n_estimators=250,contamination='auto',random_state=42)
    det.fit(Xtr[NUMERIC])
    val_scores=det.decision_function(Xte[NUMERIC])
    threshold=float(np.quantile(val_scores,0.05))
    enc=OneHotEncoder(handle_unknown='error'); enc.fit(df[['process_step']])
    MODEL_DIR.mkdir(exist_ok=True)
    joblib.dump(pipe,MODEL_DIR/'defect_pipeline.joblib'); joblib.dump(det,MODEL_DIR/'unknown_detector.joblib')
    joblib.dump(enc,MODEL_DIR/'process_step_encoder.joblib'); joblib.dump(threshold,MODEL_DIR/'unknown_threshold.joblib')
    joblib.dump(metrics,MODEL_DIR/'metrics.joblib')
    return metrics

if __name__=='__main__': print(train())
