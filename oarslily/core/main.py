from osslili import LicenseCopyrightDetector, Config

import os
import time


def _list_folders_recursive(path="."):
    paths = []
    for entry in os.listdir(path):
        full_path = os.path.join(path, entry)
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
        cache_dir=".oarslily_cache",
    )
    # Initialize detector
    detector = LicenseCopyrightDetector(config)

    paths = list_folders_recursive(directory_path)

    # Process a local directory
    paths = paths[:10]  # take only the first 10 for testing
    results = []
    for idx, p in enumerate(paths):
        print(f"Processing {idx + 1} of {len(paths)} paths.")
        result = detector.process_local_path(p)
        results.append(result)

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
