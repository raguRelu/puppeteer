import sqlite3

# Connect to the SQLite database
conn = sqlite3.connect('data_10.db', check_same_thread=False)
c = conn.cursor()

# Fetch data from the database
c.execute('SELECT * FROM data')
data = c.fetchall()

# Initialize variables for calculations
total_time = 0
total_retry_count = 0
total_login_count = 0
max_retry_count = 0
max_login_count = 0
max_time = float('-inf')
min_time = float('inf')

# Iterate through the data and perform calculations
for row in data:
    req_id, url, product_name_text, cat_id_, itemid, category_text, price_text, rating_float, evaluate_int, sold_int, time, error, retry_count, login_count = row
    total_time += float(time)
    total_retry_count += int(retry_count)
    total_login_count += int(login_count)
    max_time = max(max_time, float(time))
    min_time = min(min_time, float(time))
    # find max number of retries
    # find max number of logins
    max_retry_count = max(max_retry_count, int(retry_count))
    max_login_count = max(max_login_count, int(login_count))

# Calculate average time
avg_time = total_time / len(data) if len(data) > 0 else 0

# Print the results
print(f'Average Time: {avg_time:.2f} seconds')
print(f'Total Retry Count: {total_retry_count}')
print(f'Total Login Count: {total_login_count}')
print(f'Max Time: {max_time:.2f} seconds')
print(f'Min Time: {min_time:.2f} seconds')
print(f"Max Retry Count: {max_retry_count}")
print(f"Max Login Count: {max_login_count}")
print(f'Total Requests: {len(data)}')

# Close the database connection
conn.close()
