import os
from bs4 import BeautifulSoup
import re
import json

# Directory containing the HTML files
html_dir = "Rule Notebooks"

# Base URL for absolute links (update this to your website's base URL)
base_url = "/BIM-Casestudy/Rule%20Notebooks/"

# Example JSON for rule statuses (replace with actual data source)
rule_statuses = {
    "Chapter 5": {
        "501-General": "pass",
        "502-Definitions": "fail",
        "506-Building-Area": "pass",
    },
    "Chapter 6": {
        "601-General": "fail",
        "603-Combustible": "pass",
    },
}

# Function to extract the numeric parts (chapter and section) for sorting
def extract_numeric_parts(filename):
    numeric_parts = re.findall(r'\d+', filename)
    return [int(part) for part in numeric_parts] if numeric_parts else [float('inf')]

# Function to build the navigation structure
def build_navigation_structure(directory):
    nav_structure = {}

    for root, dirs, files in os.walk(directory):
        html_files = [f for f in files if f.endswith('.html') and f != 'index.html']
        if html_files:
            html_files = sorted(html_files, key=extract_numeric_parts)

            path_parts = os.path.relpath(root, directory).split(os.sep)
            if len(path_parts) > 1:
                chapter = path_parts[0]
                section = path_parts[1] if len(path_parts) > 1 else ""

                if chapter not in nav_structure:
                    nav_structure[chapter] = {}

                if section not in nav_structure[chapter]:
                    nav_structure[chapter][section] = []

                nav_structure[chapter][section].extend(html_files)

    return nav_structure

# Function to generate navigation HTML
def generate_navigation_html(nav_structure, rule_statuses):
    nav_html = '<nav>\n'
    nav_html += f'<a href="{base_url}index.html">Home</a>\n'

    for chapter, sections in nav_structure.items():
        chapter_status = rule_statuses.get(chapter, {}).get("status", "unknown")
        chapter_class = "green" if chapter_status == "pass" else "red"

        nav_html += f'<div class="{chapter_class}"><strong>{chapter}</strong></div>\n'

        for section, files in sections.items():
            section_status = rule_statuses.get(chapter, {}).get(section, "unknown")
            section_class = "green" if section_status == "pass" else "red"

            nav_html += f'<div class="{section_class}" style="margin-left: 20px;"><em>{section}</em></div>\n'

            for file in files:
                file_path = base_url + os.path.join(chapter, section, file).replace("\\", "/")
                display_name = file.replace(".html", "")
                nav_html += f'<div style="margin-left: 40px;"><a href="{file_path}">{display_name}</a></div>\n'

    nav_html += '</nav>\n'
    return nav_html

# Function to add navigation to all HTML files
def add_navigation():
    nav_structure = build_navigation_structure(html_dir)
    nav_html = generate_navigation_html(nav_structure, rule_statuses)

    for chapter, sections in nav_structure.items():
        for section, files in sections.items():
            for file in files:
                file_path = os.path.join(html_dir, chapter, section, file)

                with open(file_path, 'r', encoding='utf-8') as f:
                    soup = BeautifulSoup(f, 'html.parser')

                if soup.nav:
                    soup.nav.replace_with(BeautifulSoup(nav_html, 'html.parser'))
                else:
                    soup.body.insert(0, BeautifulSoup(nav_html, 'html.parser'))

                style_tag = soup.new_tag("style")
                style_tag.string = """
                nav {
                    width: 200px;
                    position: fixed;
                    left: 0;
                    top: 0;
                    bottom: 0;
                    background-color: #f4f4f4;
                    padding: 20px;
                    overflow-y: auto;
                }
                nav a {
                    display: block;
                    padding: 8px;
                    text-decoration: none;
                    color: #333;
                }
                nav a:hover {
                    background-color: #ddd;
                }
                .green {
                    color: green;
                }
                .red {
                    color: red;
                }
                body {
                    margin-left: 220px;
                }
                """
                soup.head.append(style_tag)

                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(str(soup))

# Execute the function
add_navigation()
