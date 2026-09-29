from fastapi.testclient import TestClient
from main import app
client=TestClient(app)
payload={'temperature_c':450,'pressure_torr':35,'gas_flow_sccm':150,'etch_rate_nm_min':80,'voltage_v':220,'current_ma':15,'process_step':'Etching'}
def test_prediction():
 r=client.post('/predict',json=payload); assert r.status_code==200; assert 'predicted_label' in r.json()
