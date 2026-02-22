import json
import os

file_path = 'ProjectTwoDashboard.ipynb'

if not os.path.exists(file_path):
    print(f"File {file_path} not found.")
    exit(1)

with open(file_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

found = False
# Find the cell
for cell in data['cells']:
    if cell['cell_type'] == 'code':
        source = cell['source']
        # check if this is the cell
        if any('from animal_shelter import AnimalShelter' in line for line in source):
            print("Found target cell.")
            found = True
            
            new_source = []
            
            # Iterate and replace
            skip_count = 0
            for line in source:
                if 'from animal_shelter import AnimalShelter' in line:
                    new_source.append("from AnimalShelter import AnimalShelter\n")
                elif 'username =' in line or 'password =' in line or 'host =' in line or 'port =' in line or 'db_name =' in line or 'col_name =' in line:
                    continue # Skip config lines
                elif 'db = AnimalShelter(' in line:
                     new_source.append("# Instantiate your CRUD object (connects to shelter.db by default)\n")
                     new_source.append("db = AnimalShelter()\n")
                elif '# Data / Model: connect to MongoDB' in line:
                     new_source.append("# Data / Model: connect to SQLite\n")
                else:
                    new_source.append(line)
            
            cell['source'] = new_source
            print("Cell updated.")
            break

if found:
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=1)
    print("Dashboard updated successfully.")
else:
    print("Target cell not found.")
