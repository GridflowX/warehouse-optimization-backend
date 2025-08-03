import subprocess
import os

def run(script_path):
    print(f"\nRunning {script_path}...\n")
    result = subprocess.run(
        ["python", script_path],
        capture_output=True,
        text=True
    )

    if result.stdout:
        print("STDOUT:")
        print(result.stdout)

    if result.stderr:
        print("STDERR:")
        print(result.stderr)

    if result.returncode != 0:
        print(f"Script failed: {script_path}")
        exit(result.returncode)
    else:
        print(f"Completed: {script_path}\n")


current_dir = os.path.dirname(os.path.abspath(__file__))

# Sequence of scripts
scripts = [
    os.path.join(current_dir, "exp4_Uniform_Unoptimized.py"),
    os.path.join(current_dir, "exp4_with_exp3distribution_Unoptimized.py"),
    os.path.join(current_dir, "exp4_Optimized-uniform.py"),
    os.path.join(current_dir, "exp4_Optimized-nonuniform.py"),
    os.path.join(current_dir, "truck_automated_exp4.py"),
    os.path.join(current_dir, "exp4_waiting_plot.py"),
]


for script in scripts:
    run(script)

print("All experiments completed.")
