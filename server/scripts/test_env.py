import os
from dotenv import load_dotenv, find_dotenv

def test_env():
    # Try to load .env
    env_file = find_dotenv()
    print(f"Found .env file at: {env_file}")
    
    # Load variables
    load_dotenv(env_file)
    
    # Verify API key
    api_key = os.getenv('OPENAI_API_KEY')
    if api_key:
        print("API key found:", api_key[:8] + "..." + api_key[-4:])
    else:
        print("API key not found")

if __name__ == "__main__":
    test_env() 