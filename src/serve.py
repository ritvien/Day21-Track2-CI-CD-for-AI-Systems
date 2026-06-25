from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import boto3
import joblib
import os

app = FastAPI()

GCS_BUCKET = os.environ.get("GCS_BUCKET", "")
GCS_MODEL_KEY = "models/latest/model.pkl"
MODEL_PATH = os.path.expanduser("~/models/model.pkl")

def download_model():
    """Tải file model.pkl từ AWS S3 về máy khi server khởi động."""
    if not GCS_BUCKET:
        print("GCS_BUCKET is not set. Skipping S3 download.")
        return
        
    try:
        s3 = boto3.client('s3')
        os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
        s3.download_file(GCS_BUCKET, GCS_MODEL_KEY, MODEL_PATH)
        print("Model downloaded successfully from S3!")
    except Exception as e:
        print(f"Error downloading model: {e}")

download_model()

if os.path.exists(MODEL_PATH):
    model = joblib.load(MODEL_PATH)
else:
    model = None

class PredictRequest(BaseModel):
    features: list[float]

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/predict")
def predict(req: PredictRequest):
    if len(req.features) != 12:
        raise HTTPException(status_code=400, detail="Expected 12 features (wine quality)")
        
    if model is None:
        raise HTTPException(status_code=500, detail="Model file not found!")
        
    pred = int(model.predict([req.features])[0])
    label_map = {0: "thấp", 1: "trung_bình", 2: "cao"}
    
    return {"prediction": pred, "label": label_map.get(pred, "unknown")}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
