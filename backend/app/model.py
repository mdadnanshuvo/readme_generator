from transformers import pipeline

# Load the Hugging Face text generation model
generator = pipeline("text-generation", model="gpt2")

def generate_text(prompt, max_length=150):
    """
    Generate text using the Hugging Face model.
    """
    response = generator(prompt, max_length=max_length, num_return_sequences=1)
    return response[0]["generated_text"]
