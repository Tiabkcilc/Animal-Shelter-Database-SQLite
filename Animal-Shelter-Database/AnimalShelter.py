import sqlite3
import os

class AnimalShelter(object):
    """ CRUD operations for Animal collection in SQLite """

    def __init__(self, db_path="shelter.db"):
        """
        Initialize the SQLite connection.
        """
        self.db_path = db_path
        if not os.path.exists(self.db_path):
            raise FileNotFoundError(f"Database file {self.db_path} not found.")

    def _get_connection(self):
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row  # Access columns by name
            return conn
        except sqlite3.Error as e:
            print(f"Error connecting to database: {e}")
            return None

    def _get_breed_id(self, cursor, breed_name):
        cursor.execute("SELECT id FROM Breeds WHERE name = ?", (breed_name,))
        result = cursor.fetchone()
        return result['id'] if result else None

    def _get_shelter_id(self, cursor, shelter_name):
        cursor.execute("SELECT id FROM Shelters WHERE name = ?", (shelter_name,))
        result = cursor.fetchone()
        return result['id'] if result else None
    
    def create(self, data):
        """
        Insert a document into the Animals table.
        :param data: dictionary containing key/value pairs
        :return: True if insert was successful, else False
        """
        if data is None or not isinstance(data, dict):
            raise Exception("Invalid data: must provide a non-empty dictionary.")

        conn = self._get_connection()
        if not conn:
            return False
            
        try:
            cursor = conn.cursor()
            
            # Extract foreign keys
            breed_name = data.get('breed')
            shelter_name = data.get('shelter')
            
            breed_id = self._get_breed_id(cursor, breed_name) if breed_name else None
            shelter_id = self._get_shelter_id(cursor, shelter_name) if shelter_name else None
            
            if not breed_id:
                raise ValueError(f"Breed '{breed_name}' not found.")
            if not shelter_id:
                raise ValueError(f"Shelter '{shelter_name}' not found.")
                
            # Prepare data
            # Assuming data has name, age_upon_outcome, outcome_type, outcome_subtype
            columns = ['name', 'age_upon_outcome', 'breed_id', 'shelter_id', 'outcome_type', 'outcome_subtype']
            values = [
                data.get('name'),
                data.get('age_upon_outcome'),
                breed_id,
                shelter_id,
                data.get('outcome_type'),
                data.get('outcome_subtype')
            ]
            
            query = f"INSERT INTO Animals ({', '.join(columns)}) VALUES ({', '.join(['?']*len(values))})"
            cursor.execute(query, values)
            conn.commit()
            return True
            
        except Exception as e:
            print(f"Error inserting document: {e}")
            return False
        finally:
            conn.close()

    def read(self, criteria=None):
        """
        Query documents from the collection.
        :param criteria: dictionary with key/value pair for lookup
        :return: list of matching documents, empty list if none found
        """
        conn = self._get_connection()
        if not conn:
            return []
            
        try:
            cursor = conn.cursor()
            
            # Base query with JOINs
            # Return both species and animal_type for compatibility
            query = """
                SELECT 
                    Animals.id, Animals.name, Animals.age_upon_outcome, 
                    Breeds.name as breed, Breeds.species, Breeds.species as animal_type, 
                    Shelters.name as shelter, Shelters.location_lat, Shelters.location_long,
                    Animals.outcome_type, Animals.outcome_subtype
                FROM Animals
                JOIN Breeds ON Animals.breed_id = Breeds.id
                JOIN Shelters ON Animals.shelter_id = Shelters.id
            """
            
            params = []
            conditions = []
            
            if criteria:
                for key, value in criteria.items():
                    column = None
                    if key == 'species' or key == 'animal_type':
                        column = "Breeds.species"
                    elif key == 'breed':
                        column = "Breeds.name"
                        # Handle MongoDB-style $in operator for lists
                        if isinstance(value, dict) and '$in' in value:
                             values_list = value['$in']
                             placeholders = ', '.join(['?'] * len(values_list))
                             conditions.append(f"{column} IN ({placeholders})")
                             params.extend(values_list)
                             continue
                    elif key == 'shelter':
                        column = "Shelters.name"
                    elif key in ['name', 'age_upon_outcome', 'outcome_type', 'outcome_subtype']:
                         column = f"Animals.{key}"
                    
                    if column:
                         conditions.append(f"{column} = ?")
                         params.append(value)
            
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            # Convert rows to dicts
            result_list = [dict(row) for row in rows]
            return result_list
            
        except Exception as e:
            print(f"Error reading documents: {e}")
            return []
        finally:
            conn.close()

    def update(self, criteria, new_data):
        """
        Update documents in the collection.
        :param criteria: dictionary filter for documents to update
        :param new_data: dictionary of fields to update
        :return: number of documents modified
        """
        if not criteria:
             raise Exception("Invalid update: criteria must be provided.")
        if not new_data:
             return 0 # Nothing to update

        conn = self._get_connection()
        if not conn:
            return 0
            
        try:
            cursor = conn.cursor()
            
            # Build SET clause
            set_clauses = []
            set_params = []
            
            # Handle possible foreign key updates in new_data
            if 'breed' in new_data:
                breed_id = self._get_breed_id(cursor, new_data['breed'])
                if breed_id:
                    set_clauses.append("breed_id = ?")
                    set_params.append(breed_id)
                # Remove breed from processing here as mapped? Or just iterate?
                # I'll iterate keys carefully.
            
            if 'shelter' in new_data:
                shelter_id = self._get_shelter_id(cursor, new_data['shelter'])
                if shelter_id:
                     set_clauses.append("shelter_id = ?")
                     set_params.append(shelter_id)

            for key, value in new_data.items():
                if key in ['name', 'age_upon_outcome', 'outcome_type', 'outcome_subtype']:
                    set_clauses.append(f"{key} = ?")
                    set_params.append(value)
            
            if not set_clauses:
                 # If only invalid keys passed, nothing to update
                 print("No valid fields to update.")
                 return 0

            # Build WHERE clause (reuse logic partially, but simpler to limit updates to Animals table usually)
            # The prompt implies updating 'records'. Usually applied to Animals.
            # However, criteria might reference joined tables (e.g. update all Cats).
            # SQLite UPDATE with JOIN is tricky. Standard SQL UPDATE doesn't support JOIN directly in WHERE easily without subqueries or specific syntax logic.
            # But the user might supply simple criteria.
            # For simplicity, I will first SELECT IDs of animals matching criteria, then UPDATE those IDs.
            
            # Step 1: Find IDs
            matching_animals = self.read(criteria)
            if not matching_animals:
                return 0
            
            ids_to_update = [a['id'] for a in matching_animals]
            
            if not ids_to_update:
                return 0
                
            placeholders = ', '.join(['?'] * len(ids_to_update))
            where_clause = f"id IN ({placeholders})"
            
            query = f"UPDATE Animals SET {', '.join(set_clauses)} WHERE {where_clause}"
            
            final_params = set_params + ids_to_update
            
            cursor.execute(query, final_params)
            modified_count = cursor.rowcount
            conn.commit()
            
            return modified_count
            
        except Exception as e:
            print(f"Error updating documents: {e}")
            return 0
        finally:
            conn.close()

    def delete(self, criteria):
        """
        Delete documents from the collection.
        :param criteria: dictionary filter for documents to delete
        :return: number of documents deleted
        """
        if not criteria:
            raise Exception("Invalid delete: criteria must be provided.")

        conn = self._get_connection()
        if not conn:
            return 0
            
        try:
            cursor = conn.cursor()
            
            # Step 1: Find IDs to delete (to support complex criteria like 'species': 'Cat')
            matching_animals = self.read(criteria)
            if not matching_animals:
                 return 0
            
            ids_to_delete = [a['id'] for a in matching_animals]
            placeholders = ', '.join(['?'] * len(ids_to_delete))
            
            query = f"DELETE FROM Animals WHERE id IN ({placeholders})"
            cursor.execute(query, ids_to_delete)
            deleted_count = cursor.rowcount
            conn.commit()
            
            return deleted_count
            
        except Exception as e:
            print(f"Error deleting documents: {e}")
            return 0
        finally:
            conn.close()
