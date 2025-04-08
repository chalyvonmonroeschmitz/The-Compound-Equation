import sys
import os
# Add the Source directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "Source")))
import argparse
import asyncio
import CC_Trie
import CC_Matcher
from CC_Trie import Trie
from scrapers import archive_scraper
from SuffixTrie import SuffixTrie


def run_cc_trie(function, file="Data/elements_table_v20.txt", elements_file=None, element='H', compound="NH4NO3"):
    """
    Function to run the CC_Trie script functionality.
    """
    trie = Trie()

    try:
        # Load element data from file
        elements_trie, trie = trie.read_in_dictionary(file_name=file, elements_file=elements_file)

        # Get all elements from the trie
        if (len(trie.root.children)) < 1:
            trie = elements_trie
            elements = trie.get_words()
        else:
            elements_trie = elements_trie
            elements = elements_trie.get_words()

        if(function == "chart_mass"):
            compound_weights = CC_Trie.chart_element_mass(trie, element)
            print(compound_weights)
            return

        elif(function == "create_matrix"):
            # Define x, y, z
            if (len(trie.root.children)) < 1:
                x = elements_trie.get_node(element).data[0].symbol if elements else None  # Starting element (e.g., first from the list)
                y = element  # Example element to sum recursively
                z = element  # Another example element to sum recursively
            else:
                x = trie.get_node(element).data[0].symbol if elements else None  # Starting element (e.g., first from the list)
                y = element  # Example element to sum recursively
                z = element  # Another example element to sum recursively

            if x is None:
                print("No valid elements found in the Trie.")
                return

            # Create summation matrix
            matrix = CC_Trie.create_summation_matrix(trie, elements, x, y, z)
            # Plot the resulting matrix
            CC_Trie.plot_matrix(matrix, elements)
            # Compute sum tables x, y, z for element x
            CC_Trie.plot_sum_for_single_element_x(elements, x)

        elif function == "chart_compound_mass":
            compound_masses = CC_Trie.chart_compound_mass(trie, compound)
            print(compound_masses)

    except FileNotFoundError:
        print(f"File {file} not found. Please provide a valid file path.")

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

def cc_matcher(function, file="Data/elements_table_v20.txt", elements_file=None, compounds=["CH4", "CH4", "CH4"]):
    trie = Trie()
    file_name = file

    try:
        # Load element data from file
        elements_trie, trie = trie.read_in_dictionary(file_name=file, elements_file=elements_file)

        # Get all elements from the trie
        if (len(trie.root.children)) < 1:
            elements = elements_trie.get_words()
        else:
            elements = trie.get_words()

    except FileNotFoundError:
        print(f"File {file_name} not found. Please provide a valid file path.")

    if function == "get_cc_constant":
        compound_d = CC_Matcher.Get_Mass(compounds[0])
        compound_i = CC_Matcher.Get_Mass(compounds[1])
        compound_h = CC_Matcher.Get_Mass(compounds[2])
        print(f"The C Constant value for {compounds} is {CC_Matcher.Get_C_Constant(compound_d, compound_i, compound_h)}")
    elif function == "get_mass":
        compounds = [compounds]
        formula_quantity = CC_Matcher.Get_Mass(compounds[0])
        mass = 0
        if len(trie.root.children) < 1:
            for e, q in formula_quantity.items():
                mass += (elements_trie.get(e).data[0].mass * q)
        else:
            for e, q in formula_quantity.items():
                mass += (trie.get(e).data[0].mass * q)
        print(f"molecular mass for {compounds} is {mass}")


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
    cc_trie_parser.add_argument("--function", type=str, required=True, help="functions [chart_compound_mass, get_elements, create_matrix]")
    cc_trie_parser.add_argument("--compound", type=str, required=False,
                                   help="from functions chart_compound_mass")
    cc_trie_parser.add_argument("--element", type=str, required=False,
                                help="from functions chart_element")
    cc_trie_parser.add_argument("--elements_file", type=str, required=False, help="Path to the elements file.")
    cc_trie_parser.add_argument("--file", type=str, required=False, help="Path to the elements compounds file.")

    # Subparser for cc_trie_matcher
    cc_matcher_parser = subparsers.add_parser("cc_matcher", help="--file <elements_mass_file default: elements_table_v20.txt> --compounds <list 3 formulas in brackets [compound1 compound2 compound3]>")
    cc_matcher_parser.add_argument("--function", type=str, required=False,
                                   help="functions [get_cc_constant, cohesion_matrix, constant_matrix]")
    cc_matcher_parser.add_argument("--compounds", type=str, required=False,
                                   help="Chemical Formulae of 1 or more seperated by spacing eg. 'CnO2Ca4He CH4 H20'")
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
        if args.function == "create_matrix":
            run_cc_trie(args.function, args.file, element=args.element)
        else:
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
        cc_matcher(args.function, args.file, compounds=args.compounds)

    elif args.mode == "archiver":
        search = args.search
        scraper = archive_scraper.Google_Scraper()
        driver = scraper.initChromeDriver(False)
        await scraper.google_scraper(driver, search)
        driver.close()

    return

if __name__ == "__main__":
    if len(sys.argv) == 1:
        # If no arguments are provided, show the help message
        print("No arguments provided. Showing usage instructions:")
        parser = argparse.ArgumentParser(description="usage: <mode> [cc_trie cc_trie_matcher compound_trie_suffix archiver] --<mode-options>")
        parser.print_help()
        sys.exit(1)

    # Run the main function
    asyncio.run(main())