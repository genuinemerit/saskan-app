# draw/saskan03_dall_e.py

import os

from openai import OpenAI

# Load OpenAI API key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError("Missing OpenAI API Key. Set OPENAI_API_KEY as an environment variable.")

# Initialize OpenAI client (NEW API FORMAT)
client = OpenAI(api_key=OPENAI_API_KEY)

response = client.images.generate(
    model="dall-e-3",
    prompt="A large triangular defensive barbican, sides 20 meters long, with 3 guard towers, one at each point of the triangle, projects out from medieval city walls. Many nachicolations and arrow loops. No visibl portal, gate or doorway. It is strong, stone, menacing. 3D Game Cinematic Feel, Epic 3D Videogame Graphics, Intricately Detailed, 8K Resolution, Dynamic Lighting, Unreal Engine 5, CryEngine, Trending on ArtStation, HDR, 3D Masterpiece, Unity Render, Perfect Composition detailed matte painting, deep color, fantastical, intricate detail, splash screen, complementary colors, fantasy concept art, 8k resolution",
    size="1024x1024",
    quality="standard",
    n=1,
)

image_url = response.data[0].url

print(image_url)
