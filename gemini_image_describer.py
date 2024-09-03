import os
import google.generativeai as genai

def authenticate(api_key):
    """Configures the Google Gemini API with the provided API key."""
    try:
        genai.configure(api_key=api_key)
    except Exception as e:
        print(f"Error configuring API: {e}")
        raise

def upload_to_gemini(path, mime_type=None):
    """Uploads the given file to Gemini.

    See https://ai.google.dev/gemini-api/docs/prompting_with_media
    """
    try:
        file = genai.upload_file(path, mime_type=mime_type)
        print(f"Uploaded file '{file.display_name}' as: {file.uri}")
        return file
    except Exception as e:
        print(f"Error uploading file: {e}")
        raise

def describe_image(api_key, image_name, model_params=None,):
    """Describes the content of an image using Google Gemini API.

    If the image is not found, returns 'Image not found'.

    Args:
        api_key (str): API key for authentication.
        image_name (str): Name of the image file to describe.
        model_params (dict, optional): Custom parameters for the model.
        prompt (str, optional): Custom prompt for the model.

    Returns:
        str: Description of the image or error message.
    """
    # Default model parameters
    default_params = {
        "temperature": 1,
        "top_p": 0.95,
        "top_k": 64,
        "max_output_tokens": 8192,
        "response_mime_type": "text/plain",
    }
    print(model_params)
    # Default prompt
    default_prompt = "What is in the image?\n"

    # Update model parameters and prompt if provided
    if model_params is not None:
        default_params.update(model_params)
        custom_prompt = default_params['prompt']
    else:
        custom_prompt = default_prompt

    # Authenticate with the provided API key
    try:
        authenticate(api_key)
    except Exception as e:
        return f"Authentication error: {e}"
    
    # Ensure the image is in the same directory as the script
    files = [f for f in os.listdir('./') if f.lower().endswith('.png')]
    print(files[0])
    image_path = files[0]

    if not os.path.exists(image_path):
        return "Image not found"

    # Upload the image
    try:
        image_file = upload_to_gemini(image_path, mime_type="image/jpeg")
    except Exception as e:
        return f"Error uploading image: {e}"

    # Create the model
    del default_params['prompt']
    try:
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            generation_config=default_params
        )
    except Exception as e:
        return f"Error creating model: {e}"

    # Start chat session
    
    try:
        chat_session = model.start_chat(
            history=[
                {
                    "role": "user",
                    "parts": [
                        image_file,
                    ],
                },
                {
                    "role": "user",
                    "parts": [
                        custom_prompt,
                    ],
                },
            ]
        )
        response = chat_session.send_message("INSERT_INPUT_HERE")
        return response.text
    except Exception as e:
        return f"Error during chat session: {e}"
