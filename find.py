"""
script for finding zip files that are not unzipped yet
and moving it to another folder
"""

import os

path = "./userver/samples3"
unzipped_path = f"{path}/notunzipped"
if not os.path.exists(unzipped_path):
    os.makedirs(unzipped_path)


for path, dirs, files in os.walk(path):
    not_found = []
    for file in files:
        if file.endswith(".zip"):
            file_name = file[:-4]
            print(file_name)
            if file_name not in dirs:
                not_found.append(file)
                os.rename(f"{path}/{file}", f"{unzipped_path}/{file}")

    break
print(not_found)
