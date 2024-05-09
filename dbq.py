import sqlite3

# Connect to the SQLite database
conn = sqlite3.connect('C:/Users/mdzid/Downloads/Documents/flask/crud_application_flask/crudapplication.db')

# Create a cursor object to execute SQL commands
cursor = conn.cursor()

# Execute SQL command to add a new column to the 'emp' table
cursor.execute("ALTER TABLE emp ADD COLUMN img_path TEXT;")

# Commit the transaction
conn.commit()

# Close the cursor and connection
cursor.close()
conn.close()
