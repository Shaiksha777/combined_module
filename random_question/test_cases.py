import json
from google import genai

# NOTE: Uses existing key variable name to keep compatibility
Api_key = 'AIzaSyChujUxcB3lOK3215fRXzbX26w7XuhXO8Q'
MODEL_CANDIDATES = [
    "gemini-2.0-flash",
    "gemini-1.5-flash",
    "gemini-1.5-flash-001",
]


def _build_prompt(question_text: str) -> str:
    return (
        "You are generating deterministic coding boilerplate and test cases. "
        "Return ONLY valid JSON (no markdown, no code fences). Schema: "
        "{\n"
        "  \"boiler_code\": string,\n"
        "  \"language\": one of [\"python\"],\n"
        "  \"test_cases\": [ { \"input\": string, \"expected_output\": string } ]\n"
        "}\n"
        "Guidelines:\n"
        "- Biolerplate must only be a structure to and not the answer to the question, like we find on the coding platforms such as leetcode where only a required boiler code is presented but no code which accepts the test cases"
        
        "- Boilerplate must define a function that solves the problem and a main that reads stdin and prints output.\n"
        "- Test cases must be runnable by providing the \"input\" to stdin; \"expected_output\" must match exact stdout (trimmed).\n"
        f"Question: {question_text}"
    )


def _parse_json_text(text: str) -> dict:
    """Try to parse JSON, stripping common wrappers if needed."""
    s = text.strip()
    # Remove possible markdown fences
    if s.startswith("```"):
        s = s.strip('`')
        # After stripping backticks, attempt to find first '{'
        idx = s.find('{')
        if idx != -1:
            s = s[idx:]
    # Try direct json
    return json.loads(s)


def generate_response(arg):
    """
    Accepts arg where arg[0] is the question text.
    Returns a dict: { 'boiler_code': str, 'language': str, 'test_cases': [ {input, expected_output}, ... ] }
    """
    question = arg[0]
    query = _build_prompt(question)
    last_error_text = ""

    client = genai.Client(api_key=Api_key)

    for model_name in MODEL_CANDIDATES:
        try:
            chat = client.chats.create(model=model_name)
            resp = chat.send_message(query)
            text = getattr(resp, 'text', '') or ''
            parsed = _parse_json_text(text)
            if not isinstance(parsed, dict):
                raise ValueError("Response is not a JSON object")
            parsed.setdefault('language', 'python')
            parsed.setdefault('boiler_code', '')
            parsed.setdefault('test_cases', [])
            return parsed
        except Exception as e:
            last_error_text = f"{model_name}: {e}"

    # Fallback minimal structure after trying all models
    print("Gemini chat request failed:", last_error_text)
    return {
        "boiler_code": f"# Failed to get boilerplate: {last_error_text}",
        "language": "python",
        "test_cases": []
    }

    