from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / 'data'
MODEL_DIR = BASE_DIR / 'saved_models'
REPORT_DIR = BASE_DIR / 'reports'
DB_PATH = DATA_DIR / 'wafer.db'
DATASET_PATH = DATA_DIR / 'semiconductor_wafer_defect_dataset.csv'
MODEL_VERSION = os.getenv('MODEL_VERSION', '1.0.0')

for p in (DATA_DIR, MODEL_DIR, REPORT_DIR):
    p.mkdir(parents=True, exist_ok=True)
