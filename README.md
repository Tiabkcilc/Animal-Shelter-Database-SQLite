# Animal-Shelter-Database-SQLite
### Database Design and Security Narrative

**Artifact Description**
The artifact selected for the Database category is the "Grazioso Salvare Dashboard" backend, originally developed in CS 340: Client/Server Development. This artifact is a Python-based `CRUD` (Create, Read, Update, Delete) module designed to interface with a database of animal shelter records. Originally, the application was built using `MongoDB` (a NoSQL document store) and relied on the `pymongo` driver to manage flat, JSON-like records for a web-based dashboard.

**Justification for Inclusion**
I selected this artifact because it provided the clearest opportunity to demonstrate Security Mindset and Relational Database Design. In its original state, the application contained significant security vulnerabilities, specifically hardcoded credentials, and utilized a flat data structure that resulted in data redundancy.
* **Skills Showcased:** By refactoring this artifact, I demonstrated the ability to migrate a backend system from a `NoSQL` architecture to a Relational (`SQL`) architecture using `SQLite`. This required designing a normalized schema (`3NF`) that separates data into logical tables (`Animals`, `Breeds`, `Shelters`) rather than storing everything in a single document. 



* **Improvements:** The most critical improvement was Security. I removed the hardcoded username and password strings that were embedded in the original source code, replacing them with a local, file-based `SQLite` connection that does not require exposed credentials in the script. Additionally, implementing a normalized schema improved data integrity; for example, breed names are now stored once in a lookup table rather than being repeated thousands of times across individual animal records.

**Course Outcomes Analysis**
With this enhancement, I have successfully met the course outcome to develop a security mindset that anticipates adversarial exploits in software architecture and designs to expose potential vulnerabilities, mitigate design flaws, and ensure privacy and enhanced security of data and resources.
* **Evaluation:** By identifying the hardcoded credentials as a critical vulnerability and re-architecting the application to eliminate them, I directly addressed the security outcome.
* **Outcome Updates:** Additionally, I met the outcome regarding "Innovative Techniques" in database management. Migrating from a schematic-less `MongoDB` setup to a strictly typed `SQL` schema required me to define constraints and foreign keys, ensuring that invalid data (such as an animal belonging to a non-existent shelter) cannot be entered into the system.

**Reflection on the Process**
The process of enhancing this artifact emphasized the trade-offs between flexibility (`NoSQL`) and structure (`SQL`).
* **Challenges:** A major challenge I faced during this enhancement was the lack of the original dataset. Since I no longer had access to the original CSV source file, I had to write a custom Python script to generate synthetic mock data. This required me to reverse-engineer what the data should look like based on the dashboard's requirements and programmatically insert valid relationships between the new tables.
* **Learning:** This experience reinforced the importance of normalization. In the original `MongoDB` version, updating a breed name would have required updating thousands of documents. In my enhanced `SQLite` version, I only need to update a single row in the `Breeds` table. This efficiency, combined with the removal of hardcoded secrets, highlighted how architectural choices made early in development dictate the long-term maintainability and security of a product.
