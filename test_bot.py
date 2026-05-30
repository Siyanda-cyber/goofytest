import json
import requests
import datetime
import os

# =====================
# PATH SETUP
# =====================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RULES_FILE = os.path.join(BASE_DIR, "rules.json")
SYNONYMS_FILE = os.path.join(BASE_DIR, "synonyms.json")
TEST_LOG_FILE = os.path.join(BASE_DIR, "test_results.json")
BOT_URL = "http://127.0.0.1:5000/chat"

# =====================
# LOAD JSON FILES
# =====================
def load_json(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading JSON {path}: {e}")
        return {}

rules = load_json(RULES_FILE)
synonyms = load_json(SYNONYMS_FILE)

if not rules or not synonyms:
    print("⚠️ Make sure rules.json and synonyms.json exist and are valid JSON!")
    exit(1)

# =====================
# HELPER FUNCTION TO LOG RESULTS
# =====================
def log_result(user_input, bot_reply, status="matched"):
    try:
        if not os.path.exists(TEST_LOG_FILE):
            with open(TEST_LOG_FILE, "w", encoding="utf-8") as f:
                json.dump([], f, indent=2)

        with open(TEST_LOG_FILE, "r+", encoding="utf-8") as f:
            data = json.load(f)
            data.append({
                "input": user_input,
                "reply": bot_reply,
                "status": status,
                "time": str(datetime.datetime.now())
            })
            f.seek(0)
            json.dump(data, f, indent=2)
    except Exception as e:
        print("Logging error:", e)

# =====================
# TESTING FUNCTION
# =====================
def test_bot():
    total_tests = 0
    matched = 0
    unknown = 0

    for dish, dish_synonyms in synonyms.items():
        for prompt in dish_synonyms:
            total_tests += 1
            prompt_text = prompt
            print(f"Testing: '{prompt_text}' ...", end=" ")

            try:
                response = requests.post(BOT_URL, json={"message": prompt_text}, timeout=5)
                bot_reply = response.json().get("reply", "")
            except Exception as e:
                print(f"❌ Request failed: {e}")
                log_result(prompt_text, "", status="error")
                continue

            # Determine status
            status = "matched" if dish.lower() in bot_reply.lower() else "unknown"

            if status == "matched":
                matched += 1
                print(f"✅ Matched ({dish})")
            else:
                unknown += 1
                print(f"⚠️ Unknown / Missed ({dish})")

            # Log result
            log_result(prompt_text, bot_reply, status=status)

    # =====================
    # SUMMARY
    # =====================
    print("\n=====================")
    print(f"Total tests run: {total_tests}")
    print(f"Matched: {matched}")
    print(f"Unknown / Missed: {unknown}")
    print("=====================")

# =====================
# MAIN
# =====================
if __name__ == "__main__":
    print("Starting automated bot tests...")
    test_bot()