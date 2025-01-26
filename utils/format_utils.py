from flatten_json import flatten

def convert_to_dict_list(csv_list):
    columns = csv_list[0][0].split(';')
    
    result = []
    for row in csv_list[1:]:
        values = row[0].split(';')
        # Combine the column names with the values to create a dictionary
        row_dict = dict(zip(columns, values))
        row_dict['Order ID'] = row_dict.get('Document', '')[7:]
        result.append(row_dict)
    
    return result   

def filter_out_lists_recursive(json_data):
        """
        Recursively filter out all list fields from the JSON data.
        
        Args:
        - json_data (dict): The input JSON object.
        
        Returns:
        - dict: The filtered JSON with lists removed.
        """
        if isinstance(json_data, dict):
            # Iterate through dictionary items and recursively filter out lists
            return {key: filter_out_lists_recursive(value) for key, value in json_data.items() if not isinstance(value, list)}
        elif isinstance(json_data, list):
            # If the value is a list, return an empty list to exclude it
            return []
        else:
            # For non-dictionary and non-list values, just return the value
            return json_data

def flatten_json(response_data):
    flat_json = {}
    filtered_data = filter_out_lists_recursive(response_data)
    flat_all = flatten(filtered_data)

    for section in response_data.get("data", {}).get("sections", []):
        for line in section.get("lines", []):
            left = line.get("left")
            right = line.get("right")
            
            if left and right:
                flat_json[left] = right

    return {**flat_all, **flat_json}


def flatten_list_json(list_dict):
    result = []
    for item in list_dict:
        item_flat = flatten_json(item)
        result.append(item_flat)
    return result

from datetime import datetime

def convert_timestamps_to_iso(data):
    """
    Recursively converts Unix timestamps in a dictionary or list of dictionaries
    to ISO 8601 datetime strings, but only if the date is within 2024.
    
    :param data: dict or list of dicts to process
    :return: The updated data with timestamps converted to ISO datetime strings
    """
    def convert_value(value):
        # Check if the value is a valid Unix timestamp (integer or str that looks like one)
        if isinstance(value, (int, str)) and str(value).isdigit():
            try:
                timestamp = int(value)
                # Convert timestamp to datetime
                date = datetime.utcfromtimestamp(timestamp)
                
                # Only convert if the date is within the year 2024
                if date.year >= 2024:
                    return date.isoformat() + "Z"
                else:
                    return value  # Leave value as is if not in 2024
            except (ValueError, OSError):
                # If conversion fails, return the value as is
                return value
        return value

    if isinstance(data, dict):
        return {key: convert_timestamps_to_iso(value) if isinstance(value, (dict, list)) else convert_value(value)
                for key, value in data.items()}
    elif isinstance(data, list):
        return [convert_timestamps_to_iso(item) for item in data]
    else:
        return data

