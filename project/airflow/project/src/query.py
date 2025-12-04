import psycopg2
from config import database

config = psycopg2.connect(**database)
current = config.cursor()

print("Filter by:\n1 - Name\n2 - Phone\n3 - City")
choice = input("Enter option number: ")

if choice == '1':
    name = input("Enter name: ")
    current.execute("SELECT * FROM phonebook1 WHERE name = %s", (name,))
elif choice == '2':
    phone = input("Enter phone: ")
    current.execute("SELECT * FROM phonebook1 WHERE phone = %s", (phone,))
elif choice == '3':
    city = input("Enter city: ")
    current.execute("SELECT * FROM phonebook1 WHERE city = %s", (city,))

rows = current.fetchall()
for row in rows:
    print(row)

current.close()
config.close()
