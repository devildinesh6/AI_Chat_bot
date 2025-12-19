import subprocess

MODEL_NAME = "gemma3:1b"

def get_response(user_text, history_text=""):
    try:
        # STRONGER PROMPT for Small Models
        full_prompt = f"""
You are a smart AI assistant with a perfect memory.
You are chatting with a user. YOU MUST use the HISTORY below to answer questions about them.

--- CHAT HISTORY START ---
{history_text}
--- CHAT HISTORY END ---

INSTRUCTION: 
1. If the user asks "Do you know me?", look at the HISTORY above.
2. If their name is in the history, say "Yes, you are [Name]."
3. Do not say "I don't have personal info" if the info is right there in the history.

User Question: {user_text}
Answer:
"""
        
        result = subprocess.run(
            ["ollama", "run", MODEL_NAME, full_prompt],
            capture_output=True, text=True, encoding="utf-8", errors="ignore"
        )
        
        if result.returncode != 0: 
            return "I'm having trouble thinking right now."
        
        return result.stdout.strip()

    except Exception as e:
        return f"Chat Error: {e}"