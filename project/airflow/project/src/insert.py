import psycopg2
from config import database
import csv

# Подключение к базе данных
config = psycopg2.connect(**database)
current = config.cursor()

# SQL-запрос на вставку
insert_table = '''
INSERT INTO phonebook1 (name, phone, city) VALUES (%s, %s, %s);
'''

print("Choose insert method:")
print("1 - Manual input")
print("2 - Load from CSV file")
choice = int(input("Enter 1 or 2: "))

if choice == 1:
    # Ручной ввод
    username = input('Enter name: ').strip()
    number = input('Enter phone number: ').strip()
    city = input('Enter city: ').strip()
    current.execute(insert_table, (username, number, city))
    print("Data inserted successfully.")

elif choice == 2:
    # Загрузка из CSV-файла
    phone_list = []
    with open('info.csv', newline='') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            if len(row) >= 3:
                name = row[0].strip()
                phone = row[1].strip()
                city = row[2].strip()
                phone_list.append((name, phone, city))

    current.executemany(insert_table, phone_list)
    print(f"{len(phone_list)} records inserted from CSV.")

else:
    print("Invalid choice.")

# Закрытие соединения
current.close()
config.commit()
config.close()
