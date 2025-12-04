import psycopg2
from config import database

config = psycopg2.connect(**database)
current = config.cursor()

create_table = '''
    CREATE TABLE IF NOT EXISTS phonebook1(
        name VARCHAR(255),
        phone VARCHAR(255),
        city VARCHAR(255)
    )
'''
current.execute(create_table)

current.close()
config.commit()
config.close()
()