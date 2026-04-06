from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def generate_description(user_input: str) -> str:
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are a support assistant that writes clear and professional ticket descriptions.",
                },
                {
                    "role": "user",
                    "content": f"""
You are a backend system that generates support ticket descriptions.

IMPORTANT RULES:
- Do NOT write email
- Do NOT include greetings like "Dear User"
- Do NOT include closing lines
- Only write a plain issue description
- Keep it short and professional

Issue: {user_input}

Output:
""",
                },
            ],
            temperature=0.5,
        )

        content = response.choices[0].message.content
        if content:
            return content.strip()
        else:
            return user_input

    except Exception as e:
        print("AI Error:", e)
        return user_input  # fallback
