import pandas as pd
import palimpzest as pz
import os 
from dotenv import load_dotenv
from typing import List, Tuple
import fitz 

load_dotenv()
def _parse_highlight(annot: fitz.Annot, wordlist: List[Tuple[float, float, float, float, str, int, int, int]]) -> str:
    points = annot.vertices
    quad_count = int(len(points) / 4)
    sentences = []
    for i in range(quad_count):
        # where the highlighted part is
        r = fitz.Quad(points[i * 4 : i * 4 + 4]).rect
        words = [w for w in wordlist if fitz.Rect(w[:4]).intersects(r)]
        sentences.append(" ".join(w[4] for w in words))
    sentence = " ".join(sentences)
    return sentence

def handle_page(page):
    wordlist = page.get_text("words")  # list of words on page
    wordlist.sort(key=lambda w: (w[3], w[0]))  # ascending y, then x

    highlights = []
    annot = page.first_annot
    while annot:
        if annot.type[0] == 8:
            highlights.append(_parse_highlight(annot, wordlist))
        annot = annot.next
    return highlights

def find_highlighted_text(filepath: str) -> List:
    doc = fitz.open(filepath)

    highlights = []
    for page in doc:
        highlights += handle_page(page)

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

def text_generation():
    # define the fields we wish to compute
    paper_cols = [
        {"name": "TargetChemical", "type": str, "desc": "The novel target chemical being generated"},
        {"name": "RecipeText", "type": str, "desc": "The entire word-for-word description of how to generate the chemical in the paper"},
    ]


    # lazily construct the computation to get emails about holidays sent in July
    #dataset = Dataset("testdata/matsci_pdfs/")
    dataset = pz.Dataset("testdata/matsci_highlighted_text/")
    dataset = dataset.sem_add_columns(paper_cols)
    #dataset = dataset.sem_filter("The email was sent in July")
    #dataset = dataset.sem_filter("The email is about holidays")

    # execute the computation w/the MaxQuality policy
    config = pz.QueryProcessorConfig(verbose=True)
    output = dataset.run(config)

    # display output (if using Jupyter, otherwise use print(output_df))
    output_df = output.to_df(cols=["TargetChemical", "RecipeText"])
    return output_df

def retrieve_ids():
    # define the fields we wish to compute
    paper_cols = [
        {"name": "PaperIdentifier", "type": str, "desc": "The title of the paper"},
        {"name": "TargetChemical", "type": str, "desc": "The novel target chemical being generated"},
        {"name": "RecipeText", "type": str, "desc": "The entire word-for-word description of how to generate the chemical in the paper"},
    ]


    # lazily construct the computation to get emails about holidays sent in July
    #dataset = Dataset("testdata/matsci_pdfs/")
    dataset = pz.Dataset("testdata/matsci_pdfs/")
    dataset = dataset.sem_add_columns(paper_cols)
    #dataset = dataset.sem_filter("The email was sent in July")
    #dataset = dataset.sem_filter("The email is about holidays")

    # execute the computation w/the MaxQuality policy
    config = pz.QueryProcessorConfig(verbose=True)
    output = dataset.run(config)

    print("OUTPUT IS ")
    print(output)
    # display output (if using Jupyter, otherwise use print(output_df))
    output_df = output.to_df(cols=["PaperIdentifier, TargetChemical, RecipeText"])
    print("OUTPUT _ DF")
    print(output_df)
    return output_df

#input_folder = "/Users/yashaga/palimpzest/testdata/matsci_pdfs/"
#output_folder = "/Users/yashaga/palimpzest/testdata/matsci_highlighted_text/"
#convert_all_highlighted_to_text(input_folder, output_folder)

#df1 = text_generation()
df2 = retrieve_ids()
#merged_df = pd.concat([df1, df2], axis=1)
print(df2)
df2.to_csv('recipes.csv', index=False)