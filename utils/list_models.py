import os
import toml
import google.generativeai as genai

def list_available_models():
    print("🔍 ASKING GOOGLE FOR AVAILABLE MODELS...")
    
    # 1. Load API Key
    try:
        with open(".streamlit/secrets.toml", "r") as f:
            secrets = toml.load(f)
        api_key = secrets.get("general", {}).get("GOOGLE_API_KEY") or secrets.get("GOOGLE_API_KEY")
        
        if not api_key:
            print("❌ No API Key found.")
            return

        genai.configure(api_key=api_key)
        
    except Exception as e:
        print(f"❌ Error loading secrets: {e}")
        return

    # 2. List Models
    try:
        print("\n📋 Your API Key supports these models:")
        print("-" * 40)
        found_any = False
        
        for m in genai.list_models():
            # We only care about models that can "generateContent" (Chat models)
            if 'generateContent' in m.supported_generation_methods:
                print(f"✅ {m.name}")
                found_any = True
                
        if not found_any:
            print("⚠️ No chat models found. Your key might be restricted.")
            
        print("-" * 40)
        print("Use one of the names above EXACTLY in your code.")

    except Exception as e:
        print(f"❌ Failed to list models: {e}")

if __name__ == "__main__":
    list_available_models()