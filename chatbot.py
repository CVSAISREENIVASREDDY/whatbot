import os
import logging
import google.generativeai as genai

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

try:
    # Configure the API key
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    
    # Create the model instance
    model = genai.GenerativeModel('gemini-pro-latest')
    logging.info("Successfully initialized Gemini model using google-generativeai.")

except Exception as e:
    logging.error(f"Failed to initialize the Gemini model: {e}")
    model = None

def get_gemini_response(user_query: str) -> str:
    """
    Generates a response using Google's native Python client.
    """
    if not model:
        logging.error("The Gemini model is not available.")
        return "Sorry, the chatbot is not configured correctly. Please contact support."

    try:
        # Generate the response
        response = model.generate_content(user_query)
        return response.text
    except Exception as e:
        logging.error(f"Error during model invocation: {e}")
        return "Sorry, I'm having trouble thinking right now. Please try again later."