import csv

# Function to parse log file
def parse_log_file(file_path):
    parsed_data = []
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            # Parse each line of the log file
            parts = line.strip().split(' - ')
            if len(parts) == 4:
                timestamp, username, debug_level, message = parts
                parsed_data.append([timestamp, username, debug_level, message])
            else:
                print(f"Skipping invalid line: {line}")
    return parsed_data

# Function to write parsed data to CSV
def write_to_csv(parsed_data, csv_file_path):
    with open(csv_file_path, 'w', newline='', encoding='utf-8') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(['Time', 'Username', 'Debug Level', 'Message'])  # Write header
        csv_writer.writerows(parsed_data)  # Write parsed data

# Main function
def main():
    log_file_path = 'users.log'
    csv_file_path = 'parsed_log_data_09-02-2024.csv'

    # Parse log file
    parsed_data = parse_log_file(log_file_path)

    # Write parsed data to CSV
    write_to_csv(parsed_data, csv_file_path)

if __name__ == "__main__":
    main()
