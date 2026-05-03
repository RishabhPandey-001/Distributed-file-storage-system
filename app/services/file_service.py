from app.services.chunk_service import create_chunks
from app.services.storage_service import store_chunks
import os

def save_file(file):
    """
    Main function to handle file upload:
    1. Read file
    2. Create chunks
    3. Store chunks in nodes
    4. Return metadata
    """

    try:
        # Step 1: read file content
        file_data = file.file.read()

        # Step 2: create chunks
        chunks = create_chunks(file_data, file.filename)

        # Step 3: store chunks in distributed nodes
        stored_locations = store_chunks(chunks)

        # Step 4: return metadata
        return {
            "filename": file.filename,
            "chunks": stored_locations
        }

    except Exception as e:
        return {"error": str(e)}


def get_all_files(metadata_store):
    """
    Return all uploaded files (from metadata.json or DB)
    """
    try:
        return metadata_store.get_all_files()
    except Exception as e:
        return {"error": str(e)}