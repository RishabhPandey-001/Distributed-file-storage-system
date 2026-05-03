import os
def create_chunks(file_data, filename):
    chunk_size = 1024 * 1024  # 1MB
    chunks = []

    for i in range(0, len(file_data), chunk_size):
        chunk = file_data[i:i + chunk_size]

        chunks.append({
            "name": f"{filename}_chunk_{i}",
            "data": chunk
        })

    return chunks


def merge_chunks(chunk_paths, output_path):
    with open(output_path, "wb") as output_file:
        for chunk_path in chunk_paths:
            with open(chunk_path, "rb") as chunk_file:
                output_file.write(chunk_file.read())