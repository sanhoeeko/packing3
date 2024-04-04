# Import the os and zipfile modules
import os
import zipfile

import json_modifier as jm

zip_file_name = 'alljson.zip'


def CreateZipFile(dir_path: str):
    # Create a zip file object
    zip_file = zipfile.ZipFile(zip_file_name, "w", zipfile.ZIP_DEFLATED)

    # Loop through the files in the directory
    for file in os.listdir(dir_path):
        # Check if the file has a .json extension
        if file.endswith(".json"):
            # Get the full file path
            file_path = os.path.join(dir_path, file)
            # Modify the data file
            jm.Json4SF(file_path)
            # Write the file to the zip file
            zip_file.write(file_path, file)
        else:
            # Get the full file path
            file_path = os.path.join(dir_path, file)
            # Write the file to the zip file
            zip_file.write(file_path, file)

    # Close the zip file
    zip_file.close()

    # Print a confirmation message
    print("The zip file has been created.")
