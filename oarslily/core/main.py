from osslili import LicenseCopyrightDetector, Config

import os
import time
from collections import deque
from concurrent.futures import ProcessPoolExecutor, as_completed

path_exclusion_list = [
    "@swc/helpers/_"  # swc helper files are not expected to have license files even though they have package.json files
]


def _test_exclude_path(path, exclude_paths=path_exclusion_list):
    for exclude_path in exclude_paths:
        if path.endswith(exclude_path):
            return True
    return False


def _list_folders_recursive(path="."):
    paths = []
    for entry in os.listdir(path):
        full_path = os.path.join(path, entry)

        if _test_exclude_path(full_path):
            # print(f"Excluding path: {full_path}")
            continue

        if os.path.isdir(full_path):
            paths.extend(_list_folders_recursive(full_path))
        else:
            if full_path.endswith("package.json"):
                paths.append(path)
    return paths


def list_folders_recursive(path="."):
    start_time = time.time()
    paths = _list_folders_recursive(path)
    elapsed_time = time.time() - start_time
    print(
        f"Walking took {elapsed_time:.4f} seconds to find {len(paths)} paths in path: {path}"
    )
    return paths


li_patterns = [
    "LICENSE*",
    "LICENCE*",
    # "COPYING*",
    # "NOTICE*",
    # "COPYRIGHT*",
    # "*GPL*",
    # "*COPYLEFT*",
    # "*EULA*",
    # "*COMMERCIAL*",
    # "*AGREEMENT*",
    # "*BUNDLE*",
    # "LEGAL*",
]


def main(directory_path):
    print("Hello from oarslily!")
    print(f"Scanning directory: {directory_path}")

    config = Config(
        max_recursion_depth=-1,
        verbose=True,
        debug=True,
        # similarity_threshold=0.95
        license_filename_patterns=li_patterns,
        # cache_dir=".oarslily_cache",
    )
    # Initialize detector
    detector = LicenseCopyrightDetector(config)

    paths = list_folders_recursive(directory_path)

    results = []
    max_worker = max(
        4, os.process_cpu_count() - 1  # avoid starving resources
    )  # generally assumed that I/O tasks as slow as CPU tasks

    # Track task completion times for ETA calculation
    overall_start_time = time.time()
    last_report_time = time.time()
    with ProcessPoolExecutor(max_workers=max_worker) as executor:
        print(f"Processing with max {max_worker} workers...")
        future_to_process = {
            executor.submit(detector.process_local_path, p): p for p in paths
        }
        idx = 0
        for future in as_completed(future_to_process):
            # Because we're now running them asynchronously, the results may come back out of order
            # If we need the results to be deterministically ordered, we will need to sort them later based on the path
            result = future.result(timeout=10)
            results.append(result)
            idx += 1

            # Calculate ETA
            elapsed = time.time() - overall_start_time
            avg_time = elapsed / idx
            remaining = len(paths) - idx
            eta_seconds = avg_time * remaining

            # Only report at most every second
            if time.time() - last_report_time > 1:
                last_report_time = time.time()
                print(
                    f"Progress: {idx}/{len(paths)} | "
                    f"Elapsed: {elapsed:.1f}s | "
                    f"ETA: {eta_seconds:.1f}s | "
                    f"Avg: {avg_time:.2f}s/task"
                )

        print(
            f"\nCompleted processing {len(paths)} paths in {time.time() - overall_start_time:.1f}s"
        )

    evidence = detector.generate_evidence(results)
    with open("evidence.json", "w") as f:
        f.write(evidence)
        p = os.path.realpath(f.name)
        print(f"Evidence written to {p}")

    cyclonedx = detector.generate_cyclonedx(results, format_type="json")

    with open("cyclonedx.json", "w") as f:
        f.write(cyclonedx)
        p = os.path.realpath(f.name)
        print(f"CycloneDX written to {p}")

    kissbom = detector.generate_kissbom(results)

    with open("kissbom.json", "w") as f:
        f.write(kissbom)
        p = os.path.realpath(f.name)
        print(f"kissbom written to {p}")
