from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from fastapi.responses import FileResponse
import shutil
import os
from datetime import datetime
import hashlib

from app.services.chunk_service import create_chunks, merge_chunks
from app.services.storage_service import store_chunks
from app.database.db import read_db, write_db
from app.utils.auth import get_current_user

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

UPLOAD_DIR = os.path.join(BASE_DIR, "storage", "temp")
DOWNLOAD_DIR = os.path.join(BASE_DIR, "storage", "downloads")

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(DOWNLOAD_DIR, exist_ok=True)


# 🔹 Generate file hash
def generate_hash(data):
    return hashlib.md5(data).hexdigest()


# 🔹 Upload API
@router.post("/upload")
def upload_file(file: UploadFile = File(...), user=Depends(get_current_user)):
    try:
        print("UPLOAD USER:", user)

        file_path = os.path.join(UPLOAD_DIR, file.filename)

        # Save temp file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Read file
        with open(file_path, "rb") as f:
            file_data = f.read()

        file_hash = generate_hash(file_data)

        db = read_db()

        # 🔥 Duplicate check
        for existing_file in db["files"]:
            if existing_file.get("hash") == file_hash:
                os.remove(file_path)
                return {"error": "File already exists (duplicate detected)"}

        # Create chunks
        chunks = create_chunks(file_data, file.filename)

        # Store chunks
        chunk_locations = store_chunks(chunks)

        # Remove temp file
        os.remove(file_path)

        # 🔥 Create file entry
        file_entry = {
            "filename": file.filename,
            "owner": user,
            "size": len(file_data),
            "upload_time": str(datetime.now()),
            "hash": file_hash,
            "chunks": chunk_locations
        }

        print("Saving file entry:", file_entry)

        # 🔥 Save to DB
        db["files"].append(file_entry)
        write_db(db)

        print("DB AFTER SAVE:", db)

        return {
            "message": "File uploaded and stored successfully",
            "file": file_entry
        }

    except Exception as e:
        print("UPLOAD ERROR:", str(e))
        return {"error": str(e)}


# 🔹 List Files API (User specific)
@router.get("/files")
def list_files(user=Depends(get_current_user)):
    try:
        print("LIST USER:", user)

        db = read_db()

        user_files = [f for f in db["files"] if f["owner"] == user]

        return {"files": user_files}

    except Exception as e:
        return {"error": str(e)}


# 🔹 Download API
@router.get("/download/{filename}")
def download_file(filename: str, user=Depends(get_current_user)):
    try:
        db = read_db()

        file_entry = None
        for file in db["files"]:
            if file["filename"] == filename:
                file_entry = file
                break

        if not file_entry:
            raise HTTPException(status_code=404, detail="File not found")

        # 🔒 Owner check
        if file_entry["owner"] != user:
            raise HTTPException(status_code=403, detail="Unauthorized")

        chunk_paths = []

        for chunk in file_entry["chunks"]:
            path = os.path.join(chunk["node"], chunk["chunk_name"])

            if os.path.exists(path):
                chunk_paths.append(path)

        if not chunk_paths:
            return {"error": "No chunks found"}

        # Sort chunks
        chunk_paths.sort(key=lambda x: int(x.split("_")[-1]))

        output_path = os.path.join(DOWNLOAD_DIR, filename)

        # Merge
        merge_chunks(chunk_paths, output_path)

        return FileResponse(output_path, filename=filename)

    except Exception as e:
        return {"error": str(e)}


# 🔹 Delete API
@router.delete("/delete/{filename}")
def delete_file(filename: str, user=Depends(get_current_user)):
    try:
        db = read_db()

        file_entry = None
        for file in db["files"]:
            if file["filename"] == filename:
                file_entry = file
                break

        if not file_entry:
            return {"error": "File not found"}

        # 🔒 Owner check
        if file_entry["owner"] != user:
            return {"error": "Unauthorized"}

        # Delete chunks
        for chunk in file_entry["chunks"]:
            chunk_path = os.path.join(chunk["node"], chunk["chunk_name"])

            if os.path.exists(chunk_path):
                os.remove(chunk_path)

        # Remove from DB
        db["files"].remove(file_entry)
        write_db(db)

        return {"message": f"{filename} deleted successfully"}

    except Exception as e:
        return {"error": str(e)}