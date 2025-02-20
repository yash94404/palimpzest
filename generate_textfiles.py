import find_hg
import palimpzest as pz
from palimpzest.sets import Dataset
from find_hg import find_highlighted_text
import os 
from dotenv import load_dotenv

load_dotenv()
'''
def convert_highlighted_to_text(fp):
    text = find_highlighted_text(fp)
    with open("output.txt", "w") as file:
        file.write(text)

convert_highlighted_to_text("/Users/yashaga/palimpzest/testdata/matsci_pdfs/ElectricalTransport&Synthesis_new_eaav9771.full.pdf")
'''
import os

def convert_all_highlighted_to_text(input_dir, output_dir):
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Iterate over all files in the input directory
    for filename in os.listdir(input_dir):
        if filename.endswith(".pdf"):
            input_path = os.path.join(input_dir, filename)
            output_filename = os.path.splitext(filename)[0] + ".txt"
            output_path = os.path.join(output_dir, output_filename)

            print(f"Processing {filename}...")

            # Extract highlighted text and save it
            text = find_highlighted_text(input_path)
            with open(output_path, "w") as file:
                file.write(text)

            print(f"Saved highlighted text to {output_path}\n")

# Example usage
input_folder = "/Users/yashaga/palimpzest/testdata/matsci_pdfs/"
output_folder = "/Users/yashaga/palimpzest/testdata/matsci_highlighted_text/"
convert_all_highlighted_to_text(input_folder, output_folder)
