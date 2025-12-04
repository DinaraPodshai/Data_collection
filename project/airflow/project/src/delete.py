import psycopg2
from config import database

config = psycopg2.connect(**database)
current = config.cursor()

print("Delete by:\n1 - Name\n2 - Phone")
choice = input("Enter option number: ")

if choice == '1':
    name = input("Enter name: ")
    current.execute("DELETE FROM phonebook1 WHERE name = %s", (name,))
elif choice == '2':
    phone = input("Enter phone: ")
    current.execute("DELETE FROM phonebook1 WHERE phone = %s", (phone,))

current.close()
config.commit()
config.close()
