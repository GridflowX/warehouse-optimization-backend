# import subprocess
#
# def run(script_path):
#     print(f"Running {script_path}...")
#     result = subprocess.run(["python", script_path], check=True)
#     print(f" Completed: {script_path}\n")
#
# # Sequence of scripts
# scripts = [
#     "exp1/exp1_Unoptimized.py",
#     "exp1/exp1_Optimized.py",
#     "exp1/truck_automated_exp1.py",
#     "exp1/exp1_waiting_plot.py"
# ]
#
# for script in scripts:
#     run(script)
#
# print("🎉 All experiments completed.")



import subprocess

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

# Sequence of scripts
scripts = [
    "exp5_onlyblue_Unoptimized.py",
    "exp5_withredstops_Unoptimized.py",
    "exp5_Optimized.py",
    "exp5_Optimized_withredstops.py",
    "exp5_automated.py"
]

for script in scripts:
    run(script)

print("All experiments completed.")
