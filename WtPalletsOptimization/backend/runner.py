import subprocess
import json
import os
import sys
import pandas as pd
from fastapi.responses import JSONResponse
import io

def run_algorithm():
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    algorithm_path = os.path.join(parent_dir, "wtPalletsOptimizationAlgorithm")
    main_script_path = os.path.join(algorithm_path, "run_all_exp.py")

    # Capture output in memory and write to file
    process_output = io.StringIO()

    result = subprocess.run(
        [sys.executable, main_script_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )

    # Write output to log file
    with open("output_log.txt", "w") as f:
        f.write(result.stdout)

    # Debug: print to console too
    print(result.stdout)

    if result.returncode != 0:
        raise Exception(f"Algorithm failed:\n{result.stdout.strip()}")

    return get_all_waiting_averages(base_dir=parent_dir)


def get_all_waiting_averages(base_dir):
    passenger_counts = [392, 896, 2968, 4032, 5040, 7952]
    experiments = ["exp1", "exp2", "exp3", "exp4"]
    capacities = [50, 80]
    base_path = os.path.join(base_dir)

    results = {}

    for exp in experiments:
        if exp != "exp4":
            # Handle standard format
            total_unopt = total_opt = total_bus_50 = total_bus_80 = 0
            count_unopt = count_opt = count_50 = count_80 = 0

            for p in passenger_counts:
                # Unoptimized
                unopt_file = os.path.join(base_path, f"{p}_{exp}.csv")
                if os.path.exists(unopt_file):
                    try:
                        df = pd.read_csv(unopt_file)
                        if "waiting_time" in df.columns:
                            total_unopt += df["waiting_time"].mean()
                            count_unopt += 1
                    except Exception as e:
                        print(f"Error reading {unopt_file}: {e}")

                # Optimized
                opt_file = os.path.join(base_path, f"{p}_{exp}_allocations.csv")
                if os.path.exists(opt_file):
                    try:
                        df = pd.read_csv(opt_file)
                        if "waiting_time" in df.columns:
                            total_opt += df["waiting_time"].mean()
                            count_opt += 1
                    except Exception as e:
                        print(f"Error reading {opt_file}: {e}")

                # Bus
                for cap in capacities:
                    bus_file = os.path.join(base_path, f"{exp}_passengerdata_{cap}_{p}.csv")
                    if os.path.exists(bus_file):
                        try:
                            df = pd.read_csv(bus_file)
                            if "waiting_time" in df.columns:
                                if cap == 50:
                                    total_bus_50 += df["waiting_time"].mean()
                                    count_50 += 1
                                else:
                                    total_bus_80 += df["waiting_time"].mean()
                                    count_80 += 1
                        except Exception as e:
                            print(f"Error reading {bus_file}: {e}")

            if count_unopt > 0:
                results[f"{exp}_unoptimized"] = round(total_unopt / count_unopt, 2)
            if count_opt > 0:
                results[f"{exp}_optimized"] = round(total_opt / count_opt, 2)
            if count_50 > 0:
                results[f"{exp}_truck_50"] = round(total_bus_50 / count_50, 2)
            if count_80 > 0:
                results[f"{exp}_truck_80"] = round(total_bus_80 / count_80, 2)

        else:
            # Handle exp4 special case
            total_uniform_unopt = total_uniform_opt = 0
            count_uniform_unopt = count_uniform_opt = 0

            total_nonunif_unopt = total_nonunif_opt = 0
            count_nonunif_unopt = count_nonunif_opt = 0

            total_bus_50 = total_bus_80 = count_50 = count_80 = 0

            for p in passenger_counts:
                # Uniform
                uniform_unopt = os.path.join(base_path, f"{p}_exp4_uniform.csv")
                uniform_opt = os.path.join(base_path, f"{p}_exp4_uniform_allocations.csv")

                if os.path.exists(uniform_unopt):
                    try:
                        df = pd.read_csv(uniform_unopt)
                        if "waiting_time" in df.columns:
                            total_uniform_unopt += df["waiting_time"].mean()
                            count_uniform_unopt += 1
                    except Exception as e:
                        print(f"Error reading {uniform_unopt}: {e}")

                if os.path.exists(uniform_opt):
                    try:
                        df = pd.read_csv(uniform_opt)
                        if "waiting_time" in df.columns:
                            total_uniform_opt += df["waiting_time"].mean()
                            count_uniform_opt += 1
                    except Exception as e:
                        print(f"Error reading {uniform_opt}: {e}")

                # Non-uniform
                nonunif_unopt = os.path.join(base_path, f"{p}_exp4_non-uniform.csv")
                nonunif_opt = os.path.join(base_path, f"{p}_exp4_non-uniform_allocations.csv")

                if os.path.exists(nonunif_unopt):
                    try:
                        df = pd.read_csv(nonunif_unopt)
                        if "waiting_time" in df.columns:
                            total_nonunif_unopt += df["waiting_time"].mean()
                            count_nonunif_unopt += 1
                    except Exception as e:
                        print(f"Error reading {nonunif_unopt}: {e}")

                if os.path.exists(nonunif_opt):
                    try:
                        df = pd.read_csv(nonunif_opt)
                        if "waiting_time" in df.columns:
                            total_nonunif_opt += df["waiting_time"].mean()
                            count_nonunif_opt += 1
                    except Exception as e:
                        print(f"Error reading {nonunif_opt}: {e}")

                # Truck data (same as other experiments)
                for cap in capacities:
                    bus_file = os.path.join(base_path, f"{exp}_passengerdata_{cap}_{p}.csv")
                    if os.path.exists(bus_file):
                        try:
                            df = pd.read_csv(bus_file)
                            if "waiting_time" in df.columns:
                                if cap == 50:
                                    total_bus_50 += df["waiting_time"].mean()
                                    count_50 += 1
                                else:
                                    total_bus_80 += df["waiting_time"].mean()
                                    count_80 += 1
                        except Exception as e:
                            print(f"Error reading {bus_file}: {e}")

            # Store results
            if count_uniform_unopt > 0:
                results["exp4_uniform_unoptimized"] = round(total_uniform_unopt / count_uniform_unopt, 2)
            if count_uniform_opt > 0:
                results["exp4_uniform_optimized"] = round(total_uniform_opt / count_uniform_opt, 2)

            if count_nonunif_unopt > 0:
                results["exp4_non_uniform_unoptimized"] = round(total_nonunif_unopt / count_nonunif_unopt, 2)
            if count_nonunif_opt > 0:
                results["exp4_non_uniform_optimized"] = round(total_nonunif_opt / count_nonunif_opt, 2)

            if count_50 > 0:
                results["exp4_truck_50"] = round(total_bus_50 / count_50, 2)
            if count_80 > 0:
                results["exp4_truck_80"] = round(total_bus_80 / count_80, 2)

    return JSONResponse(content=results)