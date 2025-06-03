from enum import Enum

class TextType(Enum):
    PARAGRAPH = "paragraph"
    TEXT = "text"
    BOLD = "bold"
    ITALIC = "italic"
    CODE = "code"
    CODE_BLOCK = "code_block"
    LINK = "link"
    IMAGE = "image"
    HEADING = "heading"
    QUOTE = "quote"
    UNORDERED_LIST = "unordered_list"   
    ORDERED_LIST = "ordered_list"
    BLOCKQUOTE = "blockquote"
    

class TextNode:
    def __init__(self, text, text_type, url=None):
        self.text = text
        self.text_type = text_type
        self.url = url

    def __eq__(self, other):
        if self.text == other.text and self.text_type == other.text_type and self.url == other.url:
            return True
        return False

    def __repr__(self):
        return f"TextNode({self.text}, {self.text_type.value}, {self.url})"
