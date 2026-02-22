from AnimalShelter import AnimalShelter
import os

def test_crud():
    # Ensure database exists
    if not os.path.exists("shelter.db"):
        print("Error: shelter.db not found. Run database_setup.py first.")
        return

    # Instantiate the class
    shelter = AnimalShelter()
    print("AnimalShelter instantiated.")

    # 1. Create a new animal
    print("\n--- Testing CREATE ---")
    new_animal = {
        'name': 'Test Dog',
        'breed': 'Golden Retriever',  # Must exist in Breeds table
        'shelter': 'Austin Animal Center', # Must exist in Shelters table
        'age_upon_outcome': '2 years',
        'outcome_type': 'Adoption',
        'outcome_subtype': 'Foster'
    }
    
    if shelter.create(new_animal):
        print("Success: 'Test Dog' created.")
    else:
        print("Failure: Could not create 'Test Dog'. check if breed/shelter exist.")

    # 2. Read the database to confirm matching record
    print("\n--- Testing READ ---")
    query = {'name': 'Test Dog'}
    results = shelter.read(query)
    
    if results:
        print(f"Success: Found {len(results)} record(s).")
        for r in results:
            print(r)
    else:
        print("Failure: 'Test Dog' not found.")

    # 3. Update the record
    print("\n--- Testing UPDATE ---")
    criteria = {'name': 'Test Dog'}
    new_values = {'name': 'Updated Dog', 'age_upon_outcome': '3 years'}
    
    updated_count = shelter.update(criteria, new_values)
    
    if updated_count > 0:
        print(f"Success: Updated {updated_count} record(s).")
    else:
        print("Failure: No records updated.")

    # Verify update
    print("Verifying update...")
    updated_results = shelter.read({'name': 'Updated Dog'})
    if updated_results:
        print(f"Confirmed: Found 'Updated Dog': {updated_results[0]['name']}, Age: {updated_results[0]['age_upon_outcome']}")
    else:
        print("Failure: 'Updated Dog' not found.")

    # 4. Delete the record
    print("\n--- Testing DELETE ---")
    delete_criteria = {'name': 'Updated Dog'}
    deleted_count = shelter.delete(delete_criteria)
    
    if deleted_count > 0:
        print(f"Success: Deleted {deleted_count} record(s).")
    else:
        print("Failure: No records deleted.")

    # Verify deletion
    print("Verifying deletion...")
    final_results = shelter.read({'name': 'Updated Dog'})
    if not final_results:
        print("Confirmed: 'Updated Dog' no longer exists.")
    else:
        print(f"Failure: 'Updated Dog' still exists: {final_results}")

if __name__ == "__main__":
    test_crud()
