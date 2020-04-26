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
    init_replace = re.sub(r" #\(\)", "_", fp)
    np_name = "pyramidized/" + re.sub(r"_+", "_", init_replace)
    if not os.path.isfile(np_name):
        path_components = os.path.split(np_name)
        os.makedirs(path_components[0], exist_ok=True)
        call = ["vips", "im_vips2tiff", fp, f"{np_name}:jpeg:75,tile:256x256,pyramid"]
        pyr_res = subprocess.run(call, stdout=subprocess.PIPE)
    concordance.append({"original": fp, "new": np_name})

json.dump(concordance, open("campi_files.json", "wb"))
