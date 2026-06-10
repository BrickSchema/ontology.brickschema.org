# /// script
# dependencies = [
#   "beautifulsoup4",
#   "lxml",
# ]
# ///
from bs4 import BeautifulSoup
import sys

if len(sys.argv) != 3:
    print("Usage: python add_versions.py <base> <input_file>")
    sys.exit(1)

# Define the file name of the existing HTML file
base_dir = sys.argv[1]
print(f"Check BASE_DIR: {base_dir}")
input_file = sys.argv[2]

# Read the contents of the existing HTML file
with open(input_file, 'r', encoding='utf-8') as file:
    html_content = file.read()

# Parse the HTML content with BeautifulSoup
soup = BeautifulSoup(html_content, 'lxml')

# links:
links = {
    "Release Candidate (Brick v1.5.0)": "/1.5.0",
    "Current stable (Brick v1.4)": "/",
    "Brick v1.4": "/1.4",
    "Brick v1.3": "/1.3",
}

# if the input file starts with any value from the links dict, then
# rewrite ALL data-href attributes to start with the corresponding value
print(f"Check INPUT_FILE: {input_file.removeprefix(base_dir)}")
input_file_end = input_file.removeprefix(base_dir)
version = "/"
for text, href in links.items():
    if input_file_end.startswith(href) and href != "/":
        print(f"Rewriting all data-href attributes to start with {href}")
        version = href
        for a in soup.find_all('a', {'data-href': True}):
            a['data-href'] = href + a['data-href']

select = soup.new_tag('select', {'id': 'brickVersionDropdown'})
# create options
for index,(text, href) in enumerate(links.items()):
    if href == version:
        option = soup.new_tag('option', value=href, selected='selected')
    else:
        option = soup.new_tag('option', value=href)
    option.string = text
    select.append(option)
# add the brickVersionDropdown id to the select tag
select['id'] = 'brickVersionDropdown'
label = soup.new_tag('label', {'for': 'brickVersionDropdown'})
label.string = 'Select Brick version:'
# put the label before the select tag and put them in their own div
select_div = soup.new_tag('div')
select_div.append(label)
select_div.append(select)


# when the option is selected, redirect to the selected version
script = soup.new_tag('script')
script.string = """
document.addEventListener('DOMContentLoaded', function() {
    // Check if there is a saved version in localStorage
    var savedVersion = localStorage.getItem('selectedBrickVersion');
    if (savedVersion) {
        document.getElementById('brickVersionDropdown').value = savedVersion;
    }

    document.getElementById('brickVersionDropdown').onchange = function() {
        // Save the selected version in localStorage
        localStorage.setItem('selectedBrickVersion', this.value);
        // Redirect to the selected version
        window.location.href = this.value;
    }
});"""

# Add the script to the end of the document
soup.head.append(script)

# Find the search container to insert the dropdown menu above it
search_container = soup.find('div', class_='search-container')
if search_container:
    search_container.append(select_div)

    # Write the modified content back to a new file or overwrite the existing one
    with open(sys.argv[2], 'w', encoding='utf-8') as file:
        file.write(str(soup))

    print(f"Dropdown menu added successfully to {sys.argv[1]}.")
else:
    print("Could not find the search container in the HTML file.")
    sys.exit(1)
