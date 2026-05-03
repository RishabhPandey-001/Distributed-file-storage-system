import os
def store_chunks(chunks):
    locations = []

    num_nodes = 4  # node1, node2, node3, node4

    for i, chunk in enumerate(chunks):
        primary_node = (i % num_nodes) + 1
        replica_node = ((i + 1) % num_nodes) + 1

        nodes = [primary_node, replica_node]

        for node in nodes:
            node_path = f"app/storage/node{node}"

            os.makedirs(node_path, exist_ok=True)

            file_path = os.path.join(node_path, chunk["name"])

            with open(file_path, "wb") as f:
                f.write(chunk["data"])

            locations.append({
                "chunk_name": chunk["name"],
                "node": node_path
            })

    return locations