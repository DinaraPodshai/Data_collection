import psycopg2
from config import database

config = psycopg2.connect(**database)
current = config.cursor()

print("What do you want to update?\n1 - Name\n2 - Phone")
choice = input("Enter option number: ")

if choice == '1':
    old_name = input("Enter current name: ")
    new_name = input("Enter new name: ")
    current.execute("UPDATE phonebook1 SET name = %s WHERE name = %s", (new_name, old_name))

elif choice == '2':
    name = input("Enter name: ")
    new_phone = input("Enter new phone: ")
    current.execute("UPDATE phonebook1 SET phone = %s WHERE name = %s", (new_phone, name))

current.close()
config.commit()
config.close()
