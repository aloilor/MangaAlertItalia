import os
import shutil

source_dir = 'aws_utils'
target_dirs = ['manga_scraper', 'email_alerter']

if not os.path.exists(source_dir):
    print(f"Source directory '{source_dir}' does not exist.")
    exit(1)

for target_dir in target_dirs:
    destination = os.path.join(target_dir, 'aws_utils')

    if os.path.exists(destination):
        shutil.rmtree(destination)

    try:
        shutil.copytree(source_dir, destination)
        print(f"Copied '{source_dir}' to '{target_dir}/aws_utils'")
        
    except Exception as e:
        print(f"Failed to copy '{source_dir}' to '{target_dir}': {e}")
