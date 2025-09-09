from fastapi import FastAPI
from pyngrok import ngrok
import uvicorn

app = FastAPI()

# Sample route
@app.get("/")
def home():
    return {"message": "Hello from FastAPI via ngrok!"}

if __name__ == "__main__":
    # Start ngrok tunnel on port 8000
    public_url = ngrok.connect(8000)
    print(f"Public URL: {public_url}")

    # Start FastAPI server
    uvicorn.run(app, host="0.0.0.0", port=8000)
