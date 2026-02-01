from fastapi import FastAPI

app = FastAPI(title="TenderAI API Gateway")

@app.get("/")
def root():
    return {"status": "ok", "service": "api-gateway"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}