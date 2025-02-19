import find_hg
import palimpzest as pz
from palimpzest.sets import Dataset
from find_hg import find_highlighted_text
import os 
from dotenv import load_dotenv

load_dotenv()

def convert_highlighted_to_text(fp):
    text = find_hg(fp)
    
    
# define the fields we wish to compute
paper_cols = [
    {"name": "PaperIdentifier", "type": str, "desc": "The title of the paper"},
    {"name": "TargetChemical", "type": str, "desc": "The novel target chemical being generated"},
    {"name": "RecipeText", "type": str, "desc": "The entire word-for-word description of how to generate the chemical in the paper"},
]


# lazily construct the computation to get emails about holidays sent in July
#dataset = Dataset("testdata/matsci_pdfs/")
dataset = Dataset("testdata/Sample_Papers_NLP/")
dataset = dataset.sem_add_columns(paper_cols)
#dataset = dataset.sem_filter("The email was sent in July")
#dataset = dataset.sem_filter("The email is about holidays")

# execute the computation w/the MaxQuality policy
config = pz.QueryProcessorConfig(verbose=True)
output = dataset.run(config)

# display output (if using Jupyter, otherwise use print(output_df))
output_df = output.to_df(cols=["PaperIdentifier", "TargetChemical", "RecipeText"])
print(output_df)
output_df.to_csv('recipes.csv', index=False)