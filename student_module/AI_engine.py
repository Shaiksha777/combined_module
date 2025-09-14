import os
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) 

# Define label mapping
LABELS = {0: "Human-written", 1: "AI-generated"}

def load_models(base_dir=BASE_DIR):
    path = f"{base_dir}/codeBERT"   # <-- checkpoint folder
    # Load tokenizer (try checkpoint first, else fall back to base model)
    try:
        tokenizer = AutoTokenizer.from_pretrained(path)
    except:
        tokenizer = AutoTokenizer.from_pretrained("microsoft/codebert-base")
    
    model = AutoModelForSequenceClassification.from_pretrained(path)
    model.eval()
    return tokenizer, model

def tokenize_code(code, tokenizer):
    if not code:
        return None
    return tokenizer(
        code,
        padding="max_length",
        truncation=True,
        max_length=256,
        return_tensors="pt"
    )

def predict(code, tokenizer, model):
    inputs = tokenize_code(code, tokenizer)
    if inputs is None:
        return None
    
    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits
        predicted_class = torch.argmax(logits, dim=-1).item()
    
    return predicted_class, LABELS[predicted_class]

"""# ---- Example usage ----
tokenizer, model = load_models()

sample_code = ""
    def fib(n):
        a, b = 0, 1
        seq = []
        for _ in range(n):
            seq.append(a)
            a, b = b, a+b
        return seq
""
pred_class, pred_label = predict(sample_code, tokenizer, model)

print(f"Prediction: {pred_label} (class {pred_class})")
"""