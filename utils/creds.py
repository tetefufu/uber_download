
import re

def extract_cookie_value():
    # Open the curl.txt file from the same directory as the script
    with open('curl.txt', 'r') as file:
        curl_content = file.read()

    # Regular expression pattern to match the cookie value after 'cookie:'
    pattern = r"-H\s+'cookie:\s*([^']+)'"

    # Search for the pattern in the content of the file
    match = re.search(pattern, curl_content)

    if match:
        # Extract the cookie value from the matched group
        cookie_value = match.group(1).strip()
        return cookie_value
    else:
        return None  # Return None if no match found
    

def extract_bearer_token():
    """
    Extracts the Bearer token from a file where it starts with 'Authorization: Bearer'.

    Args:
        file_path (str): Path to the text file.

    Returns:
        str: The Bearer token, or None if not found.
    """
    try:
        with open('curl.txt', 'r') as file:
            content = file.read()
            
        # Use regex to find the Bearer token
        match = re.search(r'(?:Authorization|authorization|authtoken): Bearer\s+([\w\.-]+)', content)
        if match:
            return match.group(1)
        else:
            return None
    except FileNotFoundError:
        print("File not found. Please check the file path.")
        return None
    