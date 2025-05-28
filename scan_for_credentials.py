import os
import re

# Patterns to look for (add more as needed)
patterns = [
    r'(?i)secret[_\-]?key\s*=\s*[\'"].+[\'"]',
    r'(?i)password\s*=\s*[\'"].+[\'"]',
    r'(?i)api[_\-]?key\s*=\s*[\'"].+[\'"]',
    r'(?i)token\s*=\s*[\'"].+[\'"]',
    r'(?i)access[_\-]?key\s*=\s*[\'"].+[\'"]',
    r'(?i)client[_\-]?secret\s*=\s*[\'"].+[\'"]',
    r'(?i)EMAIL_HOST_PASSWORD\s*=\s*[\'"].+[\'"]',
]

def scan_file(filepath):
    with open(filepath, encoding="utf-8") as f:
        for i, line in enumerate(f, 1):
            for pattern in patterns:
                if re.search(pattern, line):
                    print(f"{filepath}:{i}: {line.strip()}")

def scan_project(root_dir):
    for subdir, _, files in os.walk(root_dir):
        # Skip virtual environment and other unwanted directories
        if '.venv' in subdir or 'venv' in subdir:
            continue
        for file in files:
            if file.endswith(".py"):
                scan_file(os.path.join(subdir, file))

if __name__ == "__main__":
    print("Scanning for hardcoded credentials...")
    scan_project(".")
    print("Scan complete.")