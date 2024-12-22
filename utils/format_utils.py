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