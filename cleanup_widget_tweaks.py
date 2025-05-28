# Remove django-widget-tweaks usage from all HTML templates in the project
# filepath: cleanup_widget_tweaks.py

import os
import re

PROJECT_ROOT = r"c:\Users\jimmo\Documents\vscode\Jobtrack"  # Adjust if needed

def clean_template_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    changed = False
    new_lines = []
    for line in lines:
        # Remove {% load widget_tweaks %}
        if "{% load widget_tweaks %}" in line:
            changed = True
            continue
        # Remove |add_class, |attr, |append_attr filters
        new_line = re.sub(r"\|\s*(add_class|attr|append_attr):?['\"][^'\"]*['\"]?", "", line)
        if new_line != line:
            changed = True
        new_lines.append(new_line)

    if changed:
        with open(filepath, "w", encoding="utf-8") as f:
            f.writelines(new_lines)
        print(f"Cleaned: {filepath}")

def main():
    for root, dirs, files in os.walk(PROJECT_ROOT):
        for file in files:
            if file.endswith(".html"):
                clean_template_file(os.path.join(root, file))

if __name__ == "__main__":
    main()