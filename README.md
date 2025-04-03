# CC-TRIE Project

This project provides tools for working with Trie data structures and includes functionalities for creating summation matrices, plotting data, and running matching algorithms.

## Folder Structure
CC-TRIE/ ├── src/ │ ├── CC_Trie.py │ ├── CC_matcher.py │ └── main.py ├── Data/ │ └── elements_table_v20.txt ├── README.md └── requirements.txt


## How to Use
First setup your Python packages first for the required modules by running
```bash
pip install -r requirements.txt
python main.py 
```
### Running the Main Script

The `main.py` utility extension allows you to run different functionalities based on the command-line arguments provided.
The Jupyter_Scratchbook is recommended to get familiar with the set of functions as well as visually view the datasets and structures within the program I will be adding more to this in the following updates including Full Tri Cartesion Matrix as well as Networks Branching structures for further research and development

#### Usage
This script provides multiple functionalities for working with tries, suffix tries, compound cohesion constants, and web scraping. It supports the following modes:

- `cc_trie`: Perform operations on a compound trie.
- `cc_matcher`: Calculate cohesion constants for compounds.
- `compound_trie_suffix`: Work with suffix tries.
- `archiver`: Perform web scraping using a search term.

---
### Defaults
file: will revert to "Data/elements_table_v20.txt" if none is provided
compounds: will revert to default tri list if none provided

### General Syntax
Example Commands
Run cc_trie to create a matrix:
python main.py cc_trie --function <function_name> --file <file_path>

Run cc_matcher to calculate cohesion constants:
python main.py cc_matcher --function get_cc_constant --compounds "CH4 H2O CO2" --file elements_table_v20.txt

Run compound_trie_suffix to search for a suffix:
python main.py compound_trie_suffix --function search_suffix --file elements_table_v20.txt

Run archiver with a search term:
python main.py archiver --search "example search term"

This guide should help you effectively use the utility extension for its various functionalities. 
```bash
python main.py cc_trie --function <function_name> --file <file_path>
python main.py archiver --search "example search term"
python main.py cc_trie --function create_matrix --file "elements_table_v20.txt"
python main.py cc_matcher --function <function_name> --compounds <compound_list> --file "file_path"
cc_matcher --function get_mass --compounds "NH4NO3" --file Data/elements_table_v20.txt
python main.py cc_matcher --function get_cc_constant --compounds "CH4 H2O CO2" --file "Data/elements_table_v20.txt"
python main.py compound_trie_suffix --function search_suffix --file "Data/elements_table_v20.txt"
