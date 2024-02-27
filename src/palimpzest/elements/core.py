from palimpzest.elements import BytesField, NumericField, Schema, StringField

###################################################################################
# "Core" useful Schemas. These are Schemas that almost everyone will need.
# File, TextFile, Image, PDF, etc.
###################################################################################
class File(Schema):
    """
    A File is defined by two Fields:
    - the filename (string)
    - the contents of the file (bytes)
    """
    filename = StringField(desc="The UNIX-style name of the file", required=True)
    contents = BytesField(desc="The contents of the file", required=True)

class TextFile(File):
    """A text file is a File that contains only text. No binary data."""

class PDFFile(File):
    """A PDF file is a File that is a PDF. It has specialized fields, font information, etc."""
    # This class is currently very impoverished. It needs a lot more fields before it can correctly represent a PDF.
    text_contents = StringField(desc="The text-only contents of the PDF", required=True)

class ImageFile(File):
    """A file that contains an image."""

class Number(Schema):
    """Just a number. Often used for aggregates"""
    value = NumericField(desc="A single number", required=True)
