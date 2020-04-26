"""
Convert existing TIF files into pyramidized TIFs and normalize the filenames to
avoid URL trouble when servings as IIIF. Also creates a concordance of old and
new filenames.
"""

import os
import subprocess
import re
import tqdm
import json

with open("manifest.txt", "r") as manfile:
    manifest = manfile.readlines()
manifest = [x.strip() for x in manifest]

concordance = []

for fp in tqdm.tqdm(manifest):
    init_replace = re.sub(r"[ #\(\)]", "_", fp.encode("ascii", "ignore").decode())
    np_name = "pyramidized/" + re.sub(r"_+", "_", init_replace)
    np_name_standard = np_name.replace(".TIF", ".tif").replace(".TIFF", ".tif")
    if not os.path.isfile(np_name):
        path_components = os.path.split(np_name)
        os.makedirs(path_components[0], exist_ok=True)
        call = [
            "vips",
            "tiffsave",
            fp,
            np_name_standard,
            "--tile",
            "--pyramid",
            "--compression",
            "jpeg",
            "--tile-width",
            "512",
            "--tile-height",
            "512",
        ]
        pyr_res = subprocess.run(call, stdout=subprocess.PIPE)
    concordance.append({"original": fp, "new": np_name})

json.dump(concordance, open("campi_files.json", "w"))
