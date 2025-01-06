import csv

def load_ipo_data(csv_file):
    data = []
    try:
        with open(csv_file, mode='r', encoding='utf-8-sig') as file:  # Use utf-8-sig
            reader = csv.reader(file)
            headers = next(reader)  # Get the first row as headers
            
            for row in reader:
                # Combine headers and row values into a dictionary
                row_dict = dict(zip(headers, row))
                data.append(row_dict)
                
    except Exception as e:
        print(f"Error loading CSV: {e}")
    
    return data


def load_client_master_details(file_path):
    client_details = {}
    try:
        with open(file_path, mode='r', encoding='utf-8-sig') as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                # Using client_id as key to store client details
                client_details[row['client_id']] = row
    except Exception as e:
        print(f"Error loading client details CSV: {e}")
    
    return client_details

def get_client_details(client_id, client_details):
    return client_details.get(client_id, None)
