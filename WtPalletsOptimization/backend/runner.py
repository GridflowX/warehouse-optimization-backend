import subprocess
import json
import os
import sys
import pandas as pd
from fastapi.responses import JSONResponse
import io
import requests

def run_algorithm():
    try:
        # Fetch output from algo1
        r = requests.get("http://guidewayoptimization:8000/output")
        r.raise_for_status()
        guideway_data = r.json()
    
        parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        algorithm_path = os.path.join(parent_dir, "wtPalletsOptimizationAlgorithm")
        main_script_path = os.path.join(algorithm_path, "run_all_exp.py")

        env_data = json.dumps(guideway_data)

        # Set environment variables
        env = os.environ.copy()
        env["GUIDEWAY_DATA"] = env_data

        # Capture output in memory and write to file
        process_output = io.StringIO()

        result = subprocess.run(
            [sys.executable, main_script_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            env=env,
        )

        # Write output to log file
        with open("output_log.txt", "w") as f:
            f.write(result.stdout)

        # Debug: print to console too
        print(result.stdout)

        if result.returncode != 0:
            raise Exception(f"Algorithm failed:\n{result.stdout.strip()}")

        return get_all_waiting_averages(base_dir=parent_dir)

    except Exception as e:
        return {"error": str(e)}


def get_all_waiting_averages(base_dir):
    pallet_counts = [896]
    experiments = ["exp1"]
    capacities = [50, 80]
    base_path = os.path.join(base_dir)

    results = {}

    for exp in experiments:
        if exp != "exp4":
            # Handle standard format
            total_unopt = total_opt = total_small_truck = total_large_truck = 0
            count_unopt = count_opt = count_50 = count_80 = 0

            for p in pallet_counts:
                # Unoptimized
                unopt_file = os.path.join(base_path, f"{p}_{exp}.csv")
                if os.path.exists(unopt_file):
                    try:
                        df = pd.read_csv(unopt_file)
                        if "delivery_delay" in df.columns:
                            total_unopt += df["delivery_delay"].mean()
                            count_unopt += 1
                    except Exception as e:
                        print(f"Error reading {unopt_file}: {e}")

                # Optimized
                opt_file = os.path.join(base_path, f"{p}_{exp}_allocations.csv")
                if os.path.exists(opt_file):
                    try:
                        df = pd.read_csv(opt_file)
                        if "delivery_delay" in df.columns:
                            total_opt += df["delivery_delay"].mean()
                            count_opt += 1
                    except Exception as e:
                        print(f"Error reading {opt_file}: {e}")

                # Bus
                for cap in capacities:
                    pallet_file = os.path.join(base_path, f"{exp}_palletdata_{cap}_{p}.csv")
                    if os.path.exists(pallet_file):
                        try:
                            df = pd.read_csv(pallet_file)
                            if "delivery_delay" in df.columns:
                                if cap == 50:
                                    total_small_truck += df["delivery_delay"].mean()
                                    count_50 += 1
                                else:
                                    total_large_truck += df["delivery_delay"].mean()
                                    count_80 += 1
                        except Exception as e:
                            print(f"Error reading {pallet_file}: {e}")

            if count_unopt > 0:
                results[f"{exp}_unoptimized"] = round(total_unopt / count_unopt, 2)
            if count_opt > 0:
                results[f"{exp}_optimized"] = round(total_opt / count_opt, 2)
            if count_50 > 0:
                results[f"{exp}_truck_50"] = round(total_small_truck / count_50, 2)
            if count_80 > 0:
                results[f"{exp}_truck_80"] = round(total_large_truck / count_80, 2)

        else:
            # Handle exp4 special case
            total_uniform_unopt = total_uniform_opt = 0
            count_uniform_unopt = count_uniform_opt = 0

            total_nonunif_unopt = total_nonunif_opt = 0
            count_nonunif_unopt = count_nonunif_opt = 0

            total_small_truck = total_large_truck = count_50 = count_80 = 0

            for p in pallet_counts:
                # Uniform
                uniform_unopt = os.path.join(base_path, f"{p}_exp4_uniform.csv")
                uniform_opt = os.path.join(base_path, f"{p}_exp4_uniform_allocations.csv")

                if os.path.exists(uniform_unopt):
                    try:
                        df = pd.read_csv(uniform_unopt)
                        if "delivery_delay" in df.columns:
                            total_uniform_unopt += df["delivery_delay"].mean()
                            count_uniform_unopt += 1
                    except Exception as e:
                        print(f"Error reading {uniform_unopt}: {e}")

                if os.path.exists(uniform_opt):
                    try:
                        df = pd.read_csv(uniform_opt)
                        if "delivery_delay" in df.columns:
                            total_uniform_opt += df["delivery_delay"].mean()
                            count_uniform_opt += 1
                    except Exception as e:
                        print(f"Error reading {uniform_opt}: {e}")

                # Non-uniform
                nonunif_unopt = os.path.join(base_path, f"{p}_exp4_non-uniform.csv")
                nonunif_opt = os.path.join(base_path, f"{p}_exp4_non-uniform_allocations.csv")

                if os.path.exists(nonunif_unopt):
                    try:
                        df = pd.read_csv(nonunif_unopt)
                        if "delivery_delay" in df.columns:
                            total_nonunif_unopt += df["delivery_delay"].mean()
                            count_nonunif_unopt += 1
                    except Exception as e:
                        print(f"Error reading {nonunif_unopt}: {e}")

                if os.path.exists(nonunif_opt):
                    try:
                        df = pd.read_csv(nonunif_opt)
                        if "delivery_delay" in df.columns:
                            total_nonunif_opt += df["delivery_delay"].mean()
                            count_nonunif_opt += 1
                    except Exception as e:
                        print(f"Error reading {nonunif_opt}: {e}")

                # Truck data (same as other experiments)
                for cap in capacities:
                    pallet_file = os.path.join(base_path, f"{exp}_palletdata_{cap}_{p}.csv")
                    if os.path.exists(pallet_file):
                        try:
                            df = pd.read_csv(pallet_file)
                            if "delivery_delay" in df.columns:
                                if cap == 50:
                                    total_small_truck += df["delivery_delay"].mean()
                                    count_50 += 1
                                else:
                                    total_large_truck += df["delivery_delay"].mean()
                                    count_80 += 1
                        except Exception as e:
                            print(f"Error reading {pallet_file}: {e}")

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
                results["exp4_truck_50"] = round(total_small_truck / count_50, 2)
            if count_80 > 0:
                results["exp4_truck_80"] = round(total_large_truck / count_80, 2)

    return JSONResponse(content=results)