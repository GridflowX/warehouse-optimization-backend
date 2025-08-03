import subprocess
import json
import os
import sys
import csv

def run_algorithm(storage_params):
    # Get the parent directory where main_json.py is located
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    algorithm_path = os.path.join(parent_dir, "packageRetrievalAlgorithm")
    main_script = os.path.join(algorithm_path, "main.py")

    # Pass storage params as JSON string through env
    env = os.environ.copy()
    env["STORAGE_PARAMS"] = json.dumps(storage_params)

    # Run the script
    result = subprocess.run(
        [sys.executable, main_script],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        cwd=algorithm_path,
        env=env
    )

    if result.returncode != 0:
        raise RuntimeError(f"Algorithm execution failed:\n{result.stdout}")
    
    # 4. Read smart_rectangle_positions.csv
    rects_path = os.path.join(algorithm_path, "smart_rectangle_positions.csv")
    rectangles = []
    with open(rects_path, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            rectangles.append({
                "id": int(row["index"]),
                "width": int(row["width"]),
                "height": int(row["height"]),
                "x": int(row["x"]),
                "y": int(row["y"]),
                "packed": row["packed"]
            })

    # 5. Read smart_retrieval_paths.csv and map by id
    retrieval_path = os.path.join(algorithm_path, "smart_retrieval_paths.csv")
    retrieval_map = {}
    if os.path.exists(retrieval_path):
        with open(retrieval_path, newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                retrieval_map[int(row["index"])] = {
                    "step": row.get("step"),
                    "x": float(row["x"]) if row.get("x") else None,
                    "x": float(row["y"]) if row.get("y") else None,
                    "retrieval_order": json.loads(row["retrieval_order"]) if row.get("retrieval_order") else None
                }

    # 6. Merge retrieval info into rectangles
    for rect in rectangles:
        rid = rect["index"]
        if rid in retrieval_map:
            rect.update(retrieval_map[rid])

    return rectangles