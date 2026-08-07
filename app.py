@app.post("/chat")
def chat(message: str, subject: str = "general"):
    
    # Subject-specific responses (faster, no API calls)
    responses = {
        "pengajian_perniagaan": {
            "profit": "Profit is the money left after subtracting expenses from revenue.",
            "loss": "Loss occurs when expenses exceed revenue.",
            "business": "Business is an economic activity aimed at making profit.",
            "default": "That's a good question about Business Studies! Please ask about profit, loss, or business concepts."
        },
        "sains_sukan": {
            "photosynthesis": "Photosynthesis is the process where plants convert sunlight into chemical energy.",
            "muscle": "Muscles are tissues that enable movement in the body.",
            "exercise": "Exercise improves fitness and health through physical activity.",
            "default": "Great Sports Science question! Ask about photosynthesis, muscles, or exercise."
        },
        "pengajian_am": {
            "malaysia": "Malaysia is a Southeast Asian nation with diverse cultures.",
            "politics": "Political science studies government and power structures.",
            "society": "Society consists of people living together with shared values.",
            "default": "Interesting General Studies question! Ask about Malaysia, politics, or society."
        },
        "bahasa_melayu": {
            "grammar": "Grammar is the system of rules in Malay language.",
            "literature": "Malay literature includes traditional and modern works.",
            "writing": "Good writing requires clear structure and proper vocabulary.",
            "default": "Great Malay Language question! Ask about grammar, literature, or writing."
        },
        "general": {
            "study": "Effective studying involves active learning and repetition.",
            "exam": "For exam success: prepare well, get enough sleep, and manage time wisely.",
            "question": "Great question! Try asking about specific subjects.",
            "default": "That's a good question! Try selecting a specific subject for better answers."
        }
    }
    
    # Get subject responses
    subject_responses = responses.get(subject, responses["general"])
    
    # Find matching keyword in message
    message_lower = message.lower()
    for keyword, answer in subject_responses.items():
        if keyword in message_lower:
            return {
                "user_message": message,
                "bot_response": answer,
                "subject": subject
            }
    
    # Default response if no keyword matched
    return {
        "user_message": message,
        "bot_response": subject_responses["default"],
        "subject": subject
    }    }
    
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
