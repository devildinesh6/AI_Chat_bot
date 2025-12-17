import subprocess

# Configuration
MODEL_NAME = "gemma3:1b"

def generate_summary(text):
    """
    Strict summarization function. Forces short 15-word output.
    """
    if not text or str(text).strip() == "":
        return "(No text)"
    
    try:
        # Strict Prompt
        prompt = f"Summarize this in 1 sentence (max 15 words): {text}"
        
        result = subprocess.run(
            ["ollama", "run", MODEL_NAME, prompt],
            capture_output=True, 
            text=True, 
            encoding="utf-8", 
            errors="ignore"
        )
        
        if result.returncode != 0: 
            return "(Ollama Error)"
        
        # Cleanup
        summary = result.stdout.strip()
        words = summary.split()
        if len(words) > 15:
            summary = " ".join(words[:15]) + "..."
            
        return summary

    except Exception as e:
        return f"(Error: {e})"