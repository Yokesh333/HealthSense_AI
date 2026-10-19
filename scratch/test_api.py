import urllib.request
import json

data = {
    "profile": {
        "disease_context": ["alzheimers"],
        "patient_information": {"age": 70, "sex": "Male", "education": 16},
        "clinical_scores": {"mmse": 24, "cdr": 0.5},
        "cognitive_findings": {},
        "motor_findings": {},
        "symptoms": [],
        "imaging_findings": [],
        "laboratory_findings": [],
        "medications": [],
        "family_history": [],
        "missing_information": []
    }
}

req = urllib.request.Request(
    'http://127.0.0.1:8000/api/reports/analyze',
    data=json.dumps(data).encode('utf-8'),
    headers={'Content-Type': 'application/json'}
)
res = urllib.request.urlopen(req)
resp_data = json.loads(res.read())
print('Workflow:', resp_data.get('workflow'))
print('Explainability:', json.dumps(resp_data.get('explainability')))
