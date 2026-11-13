import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY not found.")

client = genai.Client(api_key=api_key)

models = [
    "gemini-3.5-flash",
    "gemini-3.5-flash-lite",
    "gemini-3.8-flash"
]

for model in models:

    print(f"\nTesting: {model}")

    try:
        response = client.models.generate_content(
            model=model,
            contents="Reply with exactly: Connection successful!"
        )

        print("SUCCESS:", response.text)

    except Exception as error:
        print("FAILED:", str(error)[:300])