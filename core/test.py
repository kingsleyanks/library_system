import os
# from xml.etree.ElementTree import indent


def scan_directory(path, indent=0):
    
    if os.path.isfile(path):
        print(" " * indent + f"{os.path.basename(path)}")
        return
    
    print(" " * indent + f"{os.path.basename(path)}/")
    for item in os.listdir(path):
        full_path = os.path.join(path, item)
        scan_directory(full_path, indent + 1)
        
scan_directory(r"I:\fullstack-course")