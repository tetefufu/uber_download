
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