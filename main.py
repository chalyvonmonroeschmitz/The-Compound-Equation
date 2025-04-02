import argparse
import math
import CC_Trie
from CC_Trie import Trie
import Trihesian_Matcher
from scrapers import archive_scraper
import asyncio


class EnhancedTrieWithGraph(Trie):
    def get_matrice_graph_with_results(self):
        """
        Create a matrix graph of all TrieNodes and compute the equation for connected nodes.
        Returns the graph and outputs of all calculations.
        """
        matrix_graph = {}  # To store connections and outputs

        def traverse_and_build(node, parent_word, parent_params):
            # Initialize a new entry for the current node
            current_node_key = parent_word  # The word represented by this node
            matrix_graph[current_node_key] = {"connections": [], "results": []}

            # Traverse children (connected nodes)
            for char, child_node in node.children.items():
                # Build the word as we traverse
                child_word = parent_word + char
                child_params = child_node.data[0] if child_node.data else {"d": [0, 0, 0], "i": [0, 0, 0],
                                                                           "h": [0, 0, 0]}

                # Connect parent to child
                matrix_graph[current_node_key]["connections"].append(child_word)

                # If there's a parent, child, and current node, calculate the equation
                if parent_params and child_params and node.data:
                    # Extract weights for the nodes involved in the equation
                    d = parent_params.get("d", [0, 0, 0])
                    i = node.data[0].get("i", [0, 0, 0])
                    h = child_params.get("h", [0, 0, 0])

                    # Calculate the formula
                    formula_result = (
                        3 * (sum(d) + sum(i) + sum(h)) + 50
                    ) * (1 / math.pi) / 1000

                    # Add the result to the matrix graph
                    matrix_graph[current_node_key]["results"].append({
                        "child": child_word,
                        "formula_result": formula_result
                    })

                # Recursively process the child's children
                traverse_and_build(child_node, child_word, child_params)

        # Start traversal from the root and build the graph and equation outputs
        traverse_and_build(self.root, "", None)
        return matrix_graph


def run_cc_trie():
    """
    Function to run the CC_Trie script functionality.
    """
    trie = Trie()

    # Load element data from file (Update file path accordingly)
    file_name = "Data/elements_table_v20.txt"
    try:
        trie = trie.read_in_dictionary(file_name)

        # Get all elements from the trie
        elements = trie.get_words()

        # Define x, y, z
        x = trie.get_node("He").data[0].symbol if elements else None  # Starting element (e.g., first from the list)
        y = "H"  # Example element to sum recursively
        z = "U"  # Another example element to sum recursively

        if x is None:
            print("No valid elements found in the Trie.")
            return

        # Create summation matrix
        matrix = CC_Trie.create_summation_matrix(trie, elements, x, y, z)
        # Plot the resulting matrix
        CC_Trie.plot_matrix(matrix, elements)
        # Compute sum tables x, y, z for element x
        CC_Trie.plot_sum_for_single_element_x(elements, x)

    except FileNotFoundError:
        print(f"File {file_name} not found. Please provide a valid file path.")



def run_trihesian_matcher():
    """
    Function to run the Trihesian_matcher script functionality.
    """
    Trihesian_Matcher.run_matcher()


async def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="--mode [google_scraper cc_trie trihesian_matcher <GENERIC FUNCTION>")
    parser.add_argument("--mode", type=str, required=True, choices=["google_scraper", "cc_trie", "trihesian_matcher, GENERIC_FUNCTION"],
                        help="Mode to run the script: 'google_scraper' or 'trihesian_matcher' or 'cc_trie' or <GENERIC_FUNCTION")
    parser.add_argument("--search", type=str, required=True,
                        help="Search term for the Google scraper (only used in specific modes).")
    args = parser.parse_args()

    if args.mode == "cc_trie":
        run_cc_trie()
    elif args.mode == "google_scraper":
        search = args.search
        scraper = archive_scraper.Google_Scraper()
        driver = scraper.initChromeDriver(False)
        await scraper.google_scraper(driver, search)
        driver.close()
    elif args.mode == "trihesian_matcher":
        run_trihesian_matcher()


if __name__ == "__main__":
    # Loop to keep main thread running
    asyncio.run(main())