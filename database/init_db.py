import sqlite3

# Connect to the database (creates it if it doesn't exist)
connection = sqlite3.connect("studexel.db")

# Create a cursor
cursor = connection.cursor()

print("Connected to StudExEl Database!")

# Save changes
connection.commit()

# Close the database
connection.close()

print("Database created successfully!")