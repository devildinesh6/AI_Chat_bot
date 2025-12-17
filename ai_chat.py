import subprocess

# Configuration
MODEL_NAME = "gemma3:1b"

def get_response(user_text):
    """
    Standard chat function. Returns a natural answer.
    """
    try:
        # Run Ollama normally
        result = subprocess.run(
            ["ollama", "run", MODEL_NAME, user_text],
            capture_output=True, 
            text=True, 
            encoding="utf-8", 
            errors="ignore"
        )
        
        if result.returncode != 0: 
            return "I'm having trouble thinking right now."
        
        return result.stdout.strip()

    except Exception as e:
        return f"Chat Error: {e}"