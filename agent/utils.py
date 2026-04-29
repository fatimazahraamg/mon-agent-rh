import os
import json

def load_candidates(folder_path="candidats"):
    candidates = []

    for file in os.listdir(folder_path):
        if file.endswith(".json"):
            path = os.path.join(folder_path, file)

            with open(path, "r") as f:
                data = json.load(f)
                data["__file__"] = file  # pour identifier
                candidates.append(data)

    return candidates