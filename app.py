from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Allow GitHub Pages & localhost
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

HF_API_KEY = os.getenv("HF_API_KEY")
HF_MODEL = "mistral-7b-instruct"  # Best free model for Q&A

@app.get("/")
def health():
    return {"status": "STPM ChatBot API Running ✅"}

@app.post("/chat")
def chat(message: str, subject: str = "general"):
    
    # Subject-specific system prompts
    prompts = {
        "pengajian_perniagaan": "You are a STPM Pengajian Perniagaan (Business Studies) expert. Answer in Malay when asked. Focus on Malaysian business context.",
        "sains_sukan": "You are a STPM Sains Sukan (Sports Science) expert. Answer in Malay. Explain physiological and biomechanical concepts.",
        "pengajian_am": "You are a STPM Pengajian Am (General Studies) expert. Answer in Malay. Cover current affairs, critical thinking.",
        "bahasa_melayu": "You are a STPM Bahasa Melayu expert. Answer in Malay. Help with literature, grammar, writing techniques.",
        "general": "You are an STPM study helper. Answer questions in Malay or English. Focus on exam preparation (70% general knowledge, 30% exam tips)."
    }
    
    system_prompt = prompts.get(subject, prompts["general"])
    
    try:
        # Hugging Face Inference API call
        api_url = f"https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.1"
        
        headers = {"Authorization": f"Bearer {HF_API_KEY}"}
        payload = {
            "inputs": f"{system_prompt}\n\nUser: {message}\n\nAssistant:",
            "parameters": {
                "max_new_tokens": 200,
                "temperature": 0.7,
            }
        }
        
        response = requests.post(api_url, headers=headers, json=payload)
        result = response.json()
        
        # Extract text from response
        if isinstance(result, list) and len(result) > 0:
            ai_response = result[0].get("generated_text", "").split("Assistant:")[-1].strip()
        else:
            ai_response = "Sorry, I couldn't generate a response. Try again!"
        
        return {
            "user_message": message,
            "bot_response": ai_response,
            "subject": subject
        }
    
    except Exception as e:
        return {"error": str(e), "message": "Backend error"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
