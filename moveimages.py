import os

samples_path = f"./userver/newer"
images_path = f"./userver/images3"
for path, dirs, files in os.walk(samples_path):
    for dir in dirs:
        images_dir = f"{images_path}/{dir}"
        samples_dir = f"{samples_path}/{dir}"
        if os.path.exists(images_dir):
            for path, dirs, files in os.walk(images_dir):
                for file in files:
                    print(file)
                    os.rename(f"{images_dir}/{file}", f"{samples_dir}/{file}")
            os.rmdir(images_dir)
