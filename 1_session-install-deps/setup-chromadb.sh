import os
import sys
import tempfile
import shutil

def get_python_version():
    return sys.version_info

def get_site_packages_root():
    # Set the site-packages root directory explicitly
    return "/home/cdsw/.local/lib/python3.9/site-packages/"

def modify_chromadb_init(site_packages_root):
    # Determine the file path for __init__.py in chromadb
    file_path = os.path.join(site_packages_root, "chromadb/__init__.py")
    if not os.path.isfile(file_path):
        print(f"The specified file does not exist: {file_path}")
        return
    
    with open(file_path, 'r') as file:
        content = file.readlines()
    
    # Remove lines containing the specific logger initialization
    content = [line for line in content if 'logger = logging.getLogger(__name__)' not in line]
    
    # The three lines to be added
    lines_to_add = [
        "__import__('pysqlite3')\n",
        "import sys\n",
        "sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')\n"
    ]
    
    # Write the new lines to a temp file
    with tempfile.NamedTemporaryFile('w', delete=False) as temp_file:
        temp_file.writelines(lines_to_add)
        temp_file.writelines(content)
        temp_file_path = temp_file.name
    
    # Move the temp file to the original location
    shutil.move(temp_file_path, file_path)
    print("Lines added successfully.")

def modify_yaml_config(site_packages_root):
    yaml_file_path = os.path.join(site_packages_root, "chromadb/log_config.yml")
    
    if not os.path.isfile(yaml_file_path):
        print(f"The specified file does not exist: {yaml_file_path}")
        return
    
    with open(yaml_file_path, 'r') as file:
        lines = file.readlines()
    
    with open(yaml_file_path, 'w') as file:
        for i, line in enumerate(lines):
            if 'uvicorn:' in line:
                if i + 1 < len(lines) and 'level: INFO' in lines[i + 1]:
                    lines[i + 1] = lines[i + 1].replace('level: INFO', 'level: ERROR')
            file.write(line)
    
    print("YAML config modified successfully.")

def main():
    python_version = get_python_version()
    print(f"Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    site_packages_root = get_site_packages_root()
    print(f"Site-packages directory: {site_packages_root}")

    modify_chromadb_init(site_packages_root)
    modify_yaml_config(site_packages_root)

if __name__ == "__main__":
    main()
