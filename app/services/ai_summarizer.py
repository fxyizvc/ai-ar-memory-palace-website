import re
from transformers import BartForConditionalGeneration, BartTokenizer
from pptx import Presentation
# --- NEW: Load Model and Tokenizer Manually ---
print("Loading BART Tokenizer and Model...")
model_name = "facebook/bart-large-cnn"
try:
    tokenizer = BartTokenizer.from_pretrained(model_name)
    model = BartForConditionalGeneration.from_pretrained(model_name)
    print("Model loaded successfully.")
except Exception as e:
    print(f"CRITICAL: Failed to load model or tokenizer. Error: {e}")
    # Set them to None so the app can still run and report errors
    tokenizer = None
    model = None

def summarize_text_with_bart(text_content: str) -> str:
    """
    Manually tokenizes, generates, and decodes a summary to avoid pipeline errors.
    """
    # First, check if the model loaded correctly on startup
    if not model or not tokenizer:
        return "Error: Summarization model is not available. Please check server logs."
        
    try:
        # Text cleaning step is still important
        cleaned_text = re.sub(r'\s+', ' ', re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text_content)).strip()
        if not cleaned_text:
            return "The PDF contained no valid text to summarize."

        # 1. Tokenize the text
        # The tokenizer converts the text into a format the model understands (input IDs)
        # We truncate the input to the model's maximum of 1024 tokens.
        inputs = tokenizer(
            [cleaned_text],
            max_length=1024,
            return_tensors="pt", # pt = PyTorch tensors
            truncation=True
        )

        # 2. Generate the summary
        # The model generates a sequence of token IDs representing the summary
        summary_ids = model.generate(
            inputs["input_ids"],
            num_beams=4,
            max_length=150,
            min_length=40,
            early_stopping=True
        )

        # 3. Decode the summary
        # The tokenizer converts the token IDs back into human-readable text
        summary = tokenizer.batch_decode(
            summary_ids,
            skip_special_tokens=True,
            clean_up_tokenization_spaces=False
        )[0] # Get the first (and only) summary from the batch

        return summary

    except Exception as e:
        print(f"A critical error occurred during manual summarization: {e}")
        return "Error: A critical error occurred during summarization. Check server logs."