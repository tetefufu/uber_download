def save_file(list_of_dicts, filepath, consistent_order=False):
    import logging
    import csv

    logging.info(f"saving {filepath}")
    if not list_of_dicts:
        raise ValueError("The list of dictionaries is empty.")

    header = []
    seen_keys = set()

    for dictionary in list_of_dicts:
        for key in dictionary.keys():
            if key not in seen_keys:
                header.append(key)
                seen_keys.add(key)

    # Ensure consistent column order by sorting if consistent_order is True
    if consistent_order:
        header = sorted(header)

    with open(filepath, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=header)
        writer.writeheader()
        writer.writerows(list_of_dicts)

    logging.info(f"saved to file {filepath}")
