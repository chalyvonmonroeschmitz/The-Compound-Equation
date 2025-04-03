import sys
import os

import periodictable

# Add the Source directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "Source")))
import argparse
import asyncio
import CC_Trie
import CC_Matcher
from CC_Trie import Trie
from scrapers import archive_scraper
from SuffixTrie import SuffixTrie
from CC_Trie import Compound


def run_cc_trie(function, file_path="Data/elements_table_v20.txt"):
    """
    Function to run the CC_Trie script functionality.
    """
    trie = Trie()

    try:
        # Load element data from file
        trie = trie.read_in_dictionary(file_path)

        # Get all elements from the trie
        elements = trie.get_words()

        if(function == "chart_mass"):
            compound_weights = CC_Trie.chart_element_mass(trie, "H")
            print(compound_weights)
            return

        if(function == "create_matrix"):
            # Define x, y, z
            x = trie.get_node("He").data[0].symbol if elements else None  # Starting element (e.g., first from the list)
            y = "H"  # Example element to sum recursively
            z = "U"  # Another example element to sum recursively

            if x is None:
                print("No valid elements found in the Trie.")
                return

            # Create summation matrix
            matrix = Trie.create_summation_matrix(trie, elements, x, y, z)
            # Plot the resulting matrix
            Trie.plot_matrix(matrix, elements)
            # Compute sum tables x, y, z for element x
            Trie.plot_sum_for_single_element_x(elements, x)

    except FileNotFoundError:
        print(f"File {file_path} not found. Please provide a valid file path.")

def run_suffix_trie(function, file_path="Data/elements_table_v20.txt"):
    """
        Main function to test the enhanced SuffixTrie with metadata (SuffixTrieData).
        """
    # Create an empty Suffix Trie
    suffix_trie = SuffixTrie()
    # Load content from the file into the trie
    suffix_trie.load_from_file(file_path)

    # Check the contents of the loaded text
    print("Text:", suffix_trie.text)

    while True:
        print("\nOptions:")
        print("1. Check if a pattern exists in the Suffix Trie")
        print("2. Get metadata (positions and frequency) for a suffix/pattern")
        print("3. Get all suffixes with a given prefix")
        print("4. Exit")

        choice = int(input("Enter your choice: "))
        if choice == 1:
            pattern = input("Enter the pattern to search for: ").strip()
            if suffix_trie.contains(pattern):
                print("Pattern exists in the Suffix Trie.")
            else:
                print("Pattern does not exist in the Suffix Trie.")
        elif choice == 2:
            pattern = input("Enter the pattern to get metadata for: ").strip()
            metadata = suffix_trie.get_suffix_metadata(pattern)
            if metadata:
                print(f"Metadata for '{pattern}': {metadata}")
            else:
                print(f"No metadata found for '{pattern}'.")
        elif choice == 3:
            prefix = input("Enter the prefix: ").strip()
            suffixes = suffix_trie.get_suffixes_with_prefix(prefix)
            print(f"Suffixes starting with '{prefix}': ")
            i = 0
            for suffix in suffixes:
                i += 1
                print(f"{i}) {suffix}")

        elif choice == 4:
            print("Exiting...")
            break
        else:
            print("Invalid choice. Try again.")

def cc_matcher(function, file_path="Data/elements_table_v20.txt", compounds=["CH4", "CH4", "CH4"], ):
    trie = Trie()
    file_name = file_path
    try:
        trie = trie.read_in_dictionary(file_name)
    except FileNotFoundError:
        print(f"File {file_name} not found. Please provide a valid file path.")

    if function == "get_cc_constant":
        compound_d = CC_Matcher.Get_Mass(compounds[0])
        compound_i = CC_Matcher.Get_Mass(compounds[1])
        compound_h = CC_Matcher.Get_Mass(compounds[2])
        print(f"C Constant value for {compounds} is {CC_Matcher.Get_Cohesion_Constant(compound_d, compound_i, compound_h)}")
    elif function == "get_mass":
        formula_quantity = CC_Matcher.Get_Mass(compounds[0])
        mass = 0
        for e, q in formula_quantity.items():
            mass += (trie.get(e).data[0].mass * q)
        print(f"molecular mass for {compounds[0]} is {mass}")

async def run_archiver(search_term=None):
    """
    Function to run the Archiver functionality.
    """
    if search_term:
        print(f"Running Archiver with search term: {search_term}")
        scraper = archive_scraper.Google_Scraper()
        driver = scraper.initChromeDriver(False)
        await scraper.google_scraper(driver, search_term)
        driver.close()
    else:
        print("missing search term")
        # Add logic for Archiver without a search term here


async def main():
    # Create the main parser
    parser = argparse.ArgumentParser(
        description="usage: <mode> [cc_trie cc_trie_matcher compound_trie_suffix archiver] --<mode-options>")
    subparsers = parser.add_subparsers(dest="mode", required=True, help="Mode to run the script.")

    # Subparser for cc_trie
    cc_trie_parser = subparsers.add_parser("cc_trie", help="Run the CC_Trie functionality.")
    cc_trie_parser.add_argument("--function", type=str, required=True, help="functions [chart_mass, get_elements, create_matrix]")
    cc_trie_parser.add_argument("--file", type=str, required=False, help="Path to the elements compounds file.")

    # Subparser for cc_trie_matcher
    cc_matcher_parser = subparsers.add_parser("cc_matcher", help="--file <elements_mass_file default: elements_table_v20.txt> --compounds <list 3 formulas in brackets [compound1 compound2 compound3]>")
    cc_matcher_parser.add_argument("--function", type=str, required=False,
                                   help="functions [get_cc_constant, cohesion_matrix, constant_matrix]")
    cc_matcher_parser.add_argument("--compounds", type=str, required=True,
                                   help="Chemical Formulas seperated by spacing eg. 'CnO2Ca4He CH4 H20'")
    cc_matcher_parser.add_argument("--file", type=str, required=False,
                                        help="Path to the elements compounds file (optional).")

    # Subparser for compound_trie_suffix
    compound_trie_suffix_parser = subparsers.add_parser("compound_trie_suffix",
                                                        help="Run the Compound Trie Suffix functionality.")
    compound_trie_suffix_parser.add_argument("--function", type=str, required=False,
                                help="functions [search_suffix, get_metadata, get_data_structure]")
    compound_trie_suffix_parser.add_argument("--file", type=str, required=False,
                                             help="Path to the elements compounds file (optional).")

    # Subparser for archiver
    archiver_parser = subparsers.add_parser("archiver", help="Run the Archiver functionality.")
    archiver_parser.add_argument("--search", type=str, required=True, help="Search term for the Archiver.")

    # Parse the arguments
    args = parser.parse_args()

    # Handle the selected mode
    if args.mode == "cc_trie":
        print(f"Running trie utility with options --function {args.function} --file {args.file}")
        run_cc_trie(args.function, args.file)

    elif args.mode == "compound_trie_suffix":
        print(f"Running Trie Suffix utility with options --file {args.file}")
        print("Loading data structure from file...")
        # Add logic for compound_trie_suffix here
        run_suffix_trie(args.function, args.file)

    elif args.mode == "cc_matcher":
        print("Running Compound Cohesion Constant Matcher...")
        compounds = args.compounds.split(" ")
        # Add logic for compound_trie_suffix here
        cc_matcher(args.function, args.file, compounds=compounds)

    elif args.mode == "archiver":
        search = args.search
        scraper = archive_scraper.Google_Scraper()
        driver = scraper.initChromeDriver(False)
        await scraper.google_scraper(driver, search)
        driver.close()

    exit(0)

if __name__ == "__main__":
    if len(sys.argv) == 1:
        # If no arguments are provided, show the help message
        print("No arguments provided. Showing usage instructions:")
        parser = argparse.ArgumentParser(description="usage: <mode> [cc_trie cc_trie_matcher compound_trie_suffix archiver] --<mode-options>")
        parser.print_help()
        sys.exit(1)

    # Run the main function
    asyncio.run(main())