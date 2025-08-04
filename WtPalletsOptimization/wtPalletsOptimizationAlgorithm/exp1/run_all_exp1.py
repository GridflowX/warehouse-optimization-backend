import subprocess
import os
import threading

def run(script_path):
    print(f"\nRunning {script_path}...\n")
    result = subprocess.run(
        ["python",  script_path],
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

# Sequence of scripts
current_dir = os.path.dirname(os.path.abspath(__file__))

# Build absolute paths to each experiment script
scripts = [
    os.path.join(current_dir, "exp1_Unoptimized.py"),
    # os.path.join(current_dir, "exp1_Optimized.py"),
    os.path.join(current_dir, "truck_automated_exp1.py"),
    os.path.join(current_dir, "truck_automated_exp1.py"),
    #os.path.join(current_dir, "exp1_waiting_plot.py"),
]

# for script in scripts:
#     run(script)

# Create threads for the first two scripts
thread1 = threading.Thread(target=run, args=(scripts[0],))
thread2 = threading.Thread(target=run, args=(scripts[1],))
thread3 = threading.Thread(target=run, args=(scripts[2],))

# Start both threads
thread1.start()
thread2.start()
thread3.start()

# Wait for both to complete
thread1.join()
thread2.join()
thread3.join()

print("All experiments completed.")
