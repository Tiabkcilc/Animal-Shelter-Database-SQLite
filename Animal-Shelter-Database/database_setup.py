import sqlite3
import random

def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except sqlite3.Error as e:
        print(e)
    return conn

def create_table(conn, create_table_sql):
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except sqlite3.Error as e:
        print(e)
        
def insert_data(conn):
    cursor = conn.cursor()
    
    # Breeds
    breeds = [
        ('Golden Retriever', 'Dog'),
        ('Siamese', 'Cat'),
        ('Labrador Retriever', 'Dog'),
        ('Persian', 'Cat'),
        ('Beagle', 'Dog'),
        ('Maine Coon', 'Cat'),
        ('Bulldog', 'Dog'),
        ('Sphynx', 'Cat'),
        ('German Shepherd', 'Dog'),
        ('Ragdoll', 'Cat'),
        ('Poodle', 'Dog'),
        ('Bengal', 'Cat'),
        ('Rottweiler', 'Dog'),
        ('British Shorthair', 'Cat'),
        ('Boxer', 'Dog')
    ]
    cursor.executemany("INSERT OR IGNORE INTO Breeds (name, species) VALUES (?, ?)", breeds)
    
    # Get Breed IDs for FK reference
    cursor.execute("SELECT id, name FROM Breeds")
    breed_rows = cursor.fetchall()
    breed_map = {row[1]: row[0] for row in breed_rows} 

    # Shelters
    shelters = [
        ('Austin Animal Center', 30.2672, -97.7431),
        ('Travis County Animal Shelter', 30.2222, -97.6666),
        ('Round Rock Animal Control', 30.5083, -97.6789),
        ('Cedar Park Animal Service', 30.5052, -97.8203),
        ('Georgetown Animal Shelter', 30.6333, -97.6772)
    ]
    cursor.executemany("INSERT OR IGNORE INTO Shelters (name, location_lat, location_long) VALUES (?, ?, ?)", shelters)
    
    # Get Shelter IDs for FK reference
    cursor.execute("SELECT id, name FROM Shelters")
    shelter_rows = cursor.fetchall()
    shelter_map = {row[1]: row[0] for row in shelter_rows}

    # Animals
    outcome_types = ['Adoption', 'Transfer', 'Return to Owner', 'Euthanasia', 'Died']
    outcome_subtypes = ['Foster', 'Partner', 'Medical', 'Behavior', 'Suffering']
    
    animals_data = []
    
    breed_names = list(breed_map.keys())
    shelter_names = list(shelter_map.keys())
    
    # Generate 30 animals
    for i in range(1, 31):
        name = f"Animal_{i}"
        age_upon_outcome = f"{random.randint(1, 15)} years"
        
        breed_name = random.choice(breed_names)
        breed_id = breed_map[breed_name]
        
        shelter_name = random.choice(shelter_names)
        shelter_id = shelter_map[shelter_name]
        
        outcome_type = random.choice(outcome_types)
        outcome_subtype = random.choice(outcome_subtypes) if random.random() > 0.5 else None
        
        animals_data.append((name, age_upon_outcome, breed_id, shelter_id, outcome_type, outcome_subtype))

    cursor.executemany("""
        INSERT OR IGNORE INTO Animals (name, age_upon_outcome, breed_id, shelter_id, outcome_type, outcome_subtype)
        VALUES (?, ?, ?, ?, ?, ?)
    """, animals_data)
    
    conn.commit()
    print("Database setup completed successfully.")

def main():
    database = "shelter.db" # This will create the file in the current directory
    
    sql_create_breeds_table = """ CREATE TABLE IF NOT EXISTS Breeds (
                                        id integer PRIMARY KEY AUTOINCREMENT,
                                        name text NOT NULL UNIQUE,
                                        species text NOT NULL
                                    ); """

    sql_create_shelters_table = """ CREATE TABLE IF NOT EXISTS Shelters (
                                        id integer PRIMARY KEY AUTOINCREMENT,
                                        name text NOT NULL UNIQUE,
                                        location_lat real,
                                        location_long real
                                    ); """

    sql_create_animals_table = """ CREATE TABLE IF NOT EXISTS Animals (
                                        id integer PRIMARY KEY AUTOINCREMENT,
                                        name text NOT NULL,
                                        age_upon_outcome text,
                                        breed_id integer NOT NULL,
                                        shelter_id integer NOT NULL,
                                        outcome_type text,
                                        outcome_subtype text,
                                        FOREIGN KEY (breed_id) REFERENCES Breeds (id),
                                        FOREIGN KEY (shelter_id) REFERENCES Shelters (id)
                                    ); """

    conn = create_connection(database)

    if conn is not None:
        create_table(conn, sql_create_breeds_table)
        create_table(conn, sql_create_shelters_table)
        create_table(conn, sql_create_animals_table)
        insert_data(conn)
        conn.close()
    else:
        print("Error! cannot create the database connection.")

if __name__ == '__main__':
    main()
