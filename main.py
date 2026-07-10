from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="BizPilot AI Backend")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Groq Client
client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

# Request Model
class ChatRequest(BaseModel):
    message: str

@app.get("/")
def home():
    return {
        "status": "online",
        "app": "BizPilot AI Backend"
    }

# ===========================
# CHAT ENDPOINT
# ===========================

@app.post("/chat")
async def chat(request: ChatRequest):

    try:

        response = client.chat.completions.create(

            model="openai/gpt-oss-20b",

            messages=[

                {
                    "role": "system",
                    "content": """
You are BizPilot AI.

You are a professional AI Business Assistant.

Help users with:
- Business Ideas
- Startups
- Marketing
- Sales
- Emails
- Business Plans
- Finance
- Productivity
- Customer Support
- HR
- Content Writing

Always answer professionally.

"""
                },

                {
                    "role": "user",
                    "content": request.message
                }

            ],

            temperature=0.7,

            max_tokens=1500

        )

        return {

            "success": True,

            "reply": response.choices[0].message.content

        }

    except Exception as e:

        return {

            "success": False,

            "error": str(e)

        }


