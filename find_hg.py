from typing import List, Tuple
import fitz  
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

    return ''.join(highlights)
if __name__ == "__main__":
    print(find_highlighted_text("/Users/yashaga/palimpzest/testdata/matsci_pdfs/ElectricalTransport&Synthesis_new_eaav9771.full.pdf"))