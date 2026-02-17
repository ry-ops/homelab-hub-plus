# Export and Import Data

The HomeLab Hub application now supports exporting and importing your entire setup to transfer between installations.

## Exporting Your Setup

To export your current configuration:

1. Make sure the backend server is running (if not already started):
   ```bash
   cd backend
   source .venv/bin/activate
   python wsgi.py
   ```

2. Send a GET request to the export endpoint:
   ```bash
   curl -X GET http://localhost:5000/inventory/export -o export.json
   ```

   Or, if you're using a browser:
   - Navigate to `http://localhost:3000/inventory/export`
   - Save the JSON response to a file named `export.json`

This will create a file `export.json` with your complete database content including:
- Hardware inventory
- Virtual machines
- Applications/services
- Storage devices
- Networks
- Miscellaneous items
- Documents

## Importing Your Setup

To import your setup to another installation:

1. Start the HomeLab Hub application on the target system (following the normal installation instructions)

2. Send a POST request with your exported data:
   ```bash
   curl -X POST http://localhost:5000/inventory/import \
        -H "Content-Type: application/json" \
        -d @export.json
   ```

**Important Notes:**
- The import will completely replace all existing data in the target database
- Make sure to backup your database before importing (the data is stored in `data/homelab-hub.db`)
- If you're using Docker, you can also use `docker cp` to copy the database file directly between containers
- The export/import functionality preserves all relationships between entities

## Using with Docker

If you're running this in Docker:
```bash
# Export from running container
docker exec -it <container_name> curl -X GET http://localhost:5000/inventory/export -o export.json

# Import to a new container
docker cp export.json <container_name>:/app/export.json
docker exec -it <container_name> curl -X POST http://localhost:5000/inventory/import \
     -H "Content-Type: application/json" \
     -d @/app/export.json
```