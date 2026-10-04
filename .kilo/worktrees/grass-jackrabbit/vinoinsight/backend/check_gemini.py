"""
Gemini connection checker for the VinoInsight wine chatbot.

Run this from the `backend` folder whenever the chatbot is giving limited or
canned answers:

    python check_gemini.py

It tells you, in order:
  1. whether backend/.env is being found and the API key is loaded,
  2. whether the google-genai library is installed,
  3. which Gemini model actually responds to your key,
  4. how the chatbot answers a set of GENERAL wine questions, and whether each
     answer came from the live AI or from the offline knowledge base.

If every line says "offline", the chatbot is not reaching Gemini and the
printed error message tells you why.
"""

import os
import sys

from dotenv import load_dotenv

load_dotenv()

SEPARATOR = "-" * 74


def main():
    print(SEPARATOR)
    print("VinoInsight chatbot - Gemini connection check")
    print(SEPARATOR)

    # --- 1. API key -------------------------------------------------------
    key = os.environ.get("GEMINI_API_KEY", "").strip()
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    print(f"1. .env file present at {env_path}: {os.path.exists(env_path)}")
    if key:
        print(f"   GEMINI_API_KEY loaded: yes (starts '{key[:6]}...', "
              f"{len(key)} chars)")
    else:
        print("   GEMINI_API_KEY loaded: NO")
        print("   -> Create backend/.env containing one line:")
        print("      GEMINI_API_KEY=your-key-here")
        print("   -> Get a free key at https://aistudio.google.com/apikey")
        return 1

    # --- 2. Library -------------------------------------------------------
    try:
        from google import genai
        print("2. google-genai library: installed")
    except ImportError:
        print("2. google-genai library: NOT installed")
        print("   -> Run: pip install google-genai python-dotenv")
        return 1

    # --- 3. Which model answers ------------------------------------------
    from wine_chatbot import MODEL_CANDIDATES

    client = genai.Client(api_key=key)
    working = None
    print("3. Testing models:")
    for model_name in MODEL_CANDIDATES:
        try:
            r = client.models.generate_content(
                model=model_name,
                contents="Say OK",
                config={"max_output_tokens": 20},
            )
            if (getattr(r, "text", "") or "").strip():
                print(f"   [OK]   {model_name}")
                working = working or model_name
            else:
                print(f"   [--]   {model_name}: empty response")
        except Exception as e:
            msg = str(e).replace("\n", " ")[:120]
            print(f"   [FAIL] {model_name}: {msg}")

    if not working:
        print("\n   No model responded. Common causes:")
        print("   - The API key is invalid, revoked, or from the wrong project.")
        print("   - The 'Generative Language API' is not enabled for the project.")
        print("   - No internet access, or a firewall/proxy is blocking")
        print("     generativelanguage.googleapis.com.")
        print("   - Free-tier quota exhausted for today.")
        return 1

    print(f"\n   Working model: {working}")

    # --- 4. Real general wine questions ----------------------------------
    from wine_chatbot import get_chat_response, get_status

    questions = [
        "What is Merlot?",
        "What wine goes with spicy chicken curry?",
        "What is the difference between Champagne and Prosecco?",
        "How long does an opened bottle of red wine last?",
        "I know nothing about wine, what should I buy first?",
        "How is wine actually made?",
        "What temperature should I serve white wine at?",
        "What does 'dry' mean on a wine label?",
    ]

    print(SEPARATOR)
    print("4. General wine questions:")
    print(SEPARATOR)
    ai_count = 0
    for q in questions:
        answer, used_ai = get_chat_response(q)
        ai_count += 1 if used_ai else 0
        tag = "AI     " if used_ai else "OFFLINE"
        print(f"\n[{tag}] Q: {q}")
        print(f"          A: {answer}")

    print("\n" + SEPARATOR)
    print(f"Live AI answers: {ai_count}/{len(questions)}")
    print(f"Status: {get_status()}")
    print(SEPARATOR)
    if ai_count == len(questions):
        print("All good - the chatbot is answering general wine questions with "
              "live AI.")
        return 0
    print("Some answers fell back to the offline knowledge base. See the error "
          "above.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
