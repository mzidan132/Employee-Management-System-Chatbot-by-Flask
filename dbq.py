import sqlite3

# Connect to the SQLite database
conn = sqlite3.connect('C:/Users/mdzid/Downloads/Documents/flask/crud_application_flask/crudapplication.db')

# Create a cursor object to execute SQL commands
cursor = conn.cursor()

# Step 1: Add the new column without a default value
cursor.execute("ALTER TABLE emp ADD COLUMN academics TEXT;")

conn.commit()

# Close the cursor and connection
cursor.close()
conn.close()
