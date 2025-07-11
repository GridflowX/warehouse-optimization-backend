import subprocess
import json
import os
import sys

def run_algorithm(alpha, beta):
    # Get the parent directory where main_json.py is located
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    main_script_path = os.path.join(parent_dir, "main_json.py")
    
    # Set environment variables
    env = os.environ.copy()
    env["ALPHA"] = str(alpha)
    env["BETA"] = str(beta)
    
    # Run the main_json.py script directly
    result = subprocess.run(
        [sys.executable, main_script_path],
        cwd=parent_dir,
        env=env,
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        raise Exception(f"Algorithm failed: {result.stderr.strip()}")
    
    # After successful run, read the generated JSON output
    json_output_path = os.path.join(parent_dir, "backend", "json_output.json")
    if os.path.exists(json_output_path):
        with open(json_output_path, "r") as f:
            return json.load(f)
    else:
        # Fallback to graph_output.json if json_output.json doesn't exist
        graph_output_path = os.path.join(parent_dir, "graph_output.json")
        if os.path.exists(graph_output_path):
            with open(graph_output_path, "r") as f:
                return json.load(f)
        else:
            raise Exception("No JSON output found after algorithm execution")
