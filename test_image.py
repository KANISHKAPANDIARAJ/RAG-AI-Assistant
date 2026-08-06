from google import genai
from google.genai import types
from dotenv import load_dotenv
import os

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

IMAGE_PATH = r"C:\Users\kanis\Downloads\images.jpg"

with open(IMAGE_PATH, "rb") as f:
    image_bytes = f.read()

response = client.models.generate_content(
    model="gemini-3.6-flash",
    contents=[
        types.Part.from_bytes(
            data=image_bytes,
            mime_type="image/jpeg"   # change to image/jpeg if it's a .jpg
        ),
        "What is shown in this image?"
    ]
)

print(response.text)