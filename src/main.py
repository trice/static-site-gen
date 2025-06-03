import re
import shutil
import os

from leafnode import LeafNode
from textnode import TextType, TextNode
from parentnode import ParentNode
from enum import Enum

class BlockType(Enum):
    PARAGRAPH = "paragraph"
    HEADING = "heading"
    CODE = "code"
    CODE_BLOCK = "code_block"
    QUOTE = "quote"
    UNORDERED_LIST = "unordered_list"
    ORDERED_LIST = "ordered_list"
    BLOCKQUOTE = "blockquote"


def __internal_extract_images_or_links(text, regex):
    """
    Use the regex to extract images or links from the text.
    :param text: The text to extract images or links from
    :param regex: The regex to use to extract images or links
    :return: returns a list of tuples containing alt text and url
    """
    return re.findall(regex, text)


def extract_markdown_images(text):
    return __internal_extract_images_or_links(text, r"!\[([^\]]*)\]\(([^)]*)\)")


def extract_markdown_links(text):
    return __internal_extract_images_or_links(text, r"\[([^\]]*)\]\(([^)]*)\)")


def split_nodes_image(old_nodes):
    """
    Splits text nodes containing markdown image links into separate text and image nodes.

    This function processes a list of nodes containing textual content, where some text
    nodes may have inline markdown image links (e.g., `![alt text](image_url)`).
    It splits such nodes into separate text and image nodes, preserving their order.
    The resulting list will contain `TextNode` objects with either plain text or image
    URL content and their corresponding types (`TextType.TEXT` or `TextType.IMAGE`).

    :param old_nodes: A list of nodes, each containing textual content that may include
        markdown image links.
    :type old_nodes: list
    :return: A new list of nodes where markdown image links are split into distinct
        image nodes with their respective URLs and alternative texts.
    :rtype: list
    """
    new_nodes = []
    for old_node in old_nodes:
        if old_node.text_type != TextType.TEXT:
            new_nodes.append(old_node)
            continue
            
        new_text, _ = re.subn(r"(!\[[^]]*]\([^)]*\))", "-*-"+r"\1"+"-*-", old_node.text)
        split_text = new_text.split("-*-")
        for index in range(len(split_text)):
            if index % 2 == 0:
                if "" != split_text[index]:
                    new_nodes.append(TextNode(split_text[index], TextType.TEXT))
            else:
                url = extract_markdown_images(split_text[index])
                new_nodes.append(TextNode(url[0][0], TextType.IMAGE, url[0][1]))
       
    return new_nodes

def split_nodes_link(old_nodes):
    """
    Splits the text of nodes containing Markdown links into separate nodes while maintaining 
    the structure of the original content. Each Markdown link in a text is isolated, and the 
    resulting split content is used to create a series of nodes, distinguished as plain text 
    or link types.

    :param old_nodes: A list of nodes, where each node is expected to contain text that 
                      may or may not include Markdown links.
    :type old_nodes: list[TextNode]
    :return: A list of newly created nodes where Markdown links in the text have been 
             split into individual link nodes, and the other text is represented as text nodes.
    :rtype: list[TextNode]
    """
    new_nodes = []
    for old_node in old_nodes:
        if old_node.text_type != TextType.TEXT:
            new_nodes.append(old_node)
            continue
            
        new_text, _ = re.subn(r"(\[[^]]*]\([^)]*\))", "-*-"+r"\1"+"-*-", old_node.text)
        split_text = new_text.split("-*-")
        for index in range(len(split_text)):
            if index % 2 == 0:
                if "" != split_text[index]:
                    new_nodes.append(TextNode(split_text[index], TextType.TEXT))
            else:
                url = extract_markdown_links(split_text[index])
                new_nodes.append(TextNode(url[0][0], TextType.LINK, url[0][1]))

    return new_nodes


def split_nodes_delimiter(old_nodes, delimiter, text_type):
    """Split text nodes based on the specified delimiter and convert them to appropriate text types.
    
    Args:
        old_nodes: List of TextNode objects to process
        delimiter: String delimiter to split text on (can be \`, **, or _)
        text_type: The TextType enum value for the resulting text type
        
    Returns:
        List of new TextNode objects after splitting and converting based on delimiters
        
    Raises:
        ValueError: If an invalid delimiter is provided
    """
    # Define valid delimiters and their corresponding text types
    valid_delimiters = ["`", "**", "_"]

    # Validate the delimiter
    if delimiter not in valid_delimiters:
        raise ValueError(f"invalid delimiter: {delimiter}")

    # Process nodes based on their type and delimiter
    # Delimiters should be processed in order: code, bold, italic
    # This handles cases like **kwargs and _ in Python code
    new_nodes = []
    for node in old_nodes:
        # check if there is a pair of delimiter characters
        if node.text.count(delimiter) % 2 != 0:
            raise Exception(f"missing delimiter {delimiter} in {node.text}")

        # Skip processing if the node is not a TEXT type
        if node.text_type != TextType.TEXT:
            new_nodes.append(node)
        else:
            # Split text into chunks using the delimiter
            chunks = node.text.split(delimiter)
            for index in range(0, len(chunks)):
                # Even indices are regular text, odd indices are formatted text
                if index % 2 == 0:
                    if "" != chunks[index]:
                        new_nodes.append(TextNode(chunks[index], TextType.TEXT))
                else:
                    new_nodes.append(TextNode(chunks[index], text_type))

    return new_nodes


def heading_text_to_heading_leafnode(text_node):
    # Count the #s then make a leafnode by splitting off the #s
    heading_level = text_node.text.count("#")
    if heading_level > 6:
        raise Exception("heading level must be <= 6")
    heading_text = text_node.text.replace("#" * heading_level, "").strip()
    return LeafNode("h" + str(heading_level), heading_text)


def code_block_to_code_parent_node(text_node):
    split_text = text_node.text.split("```")
    if len(split_text) != 3:
        raise Exception("code block must have 3 backticks")
    nodes = [LeafNode("code", split_text[1].strip())]
    return ParentNode("pre", nodes)


def text_node_to_html_node(text_node):
    """
    Converts a `text_node` object into an appropriate HTML node representation based on 
    the type of text it contains. This function maps specific text types such as plain 
    text, bold, italic, code, link, and images to their corresponding HTML elements.

    :param text_node: The input object contains information about the text and its type.
                      It must include attributes such as `text_type`, `text`, and for 
                      certain types, `url`.

    :return: An instance of `LeafNode` is representing the equivalent HTML node for the 
             provided `text_node` configuration.

    :raises Exception: If the `text_node` contains an unsupported or unknown `text_type`.
    """
    if text_node.text_type == TextType.TEXT:
        return LeafNode(None, text_node.text)
    elif text_node.text_type == TextType.BOLD:
        return LeafNode("b", text_node.text)
    elif text_node.text_type == TextType.ITALIC:
        return LeafNode("i", text_node.text)
    elif text_node.text_type == TextType.CODE:
        return LeafNode("code", text_node.text)
    elif text_node.text_type == TextType.CODE_BLOCK:
        return code_block_to_code_parent_node(text_node)
    elif text_node.text_type == TextType.LINK:
        return LeafNode("a", text_node.text, props={"href": text_node.url})
    elif text_node.text_type == TextType.IMAGE:
        return LeafNode("img", text_node.text, props={"src": text_node.url})
    elif text_node.text_type == TextType.HEADING:
        # This needs to call a method to build a heading tag based on the number of #s in the text
        return heading_text_to_heading_leafnode(text_node)
    elif text_node.text_type == TextType.QUOTE:
        return LeafNode("q", text_node.text)
    elif text_node.text_type == TextType.UNORDERED_LIST:
        # I think this gets complicated because we need to use a li tag for unordered lists
        return LeafNode("li", text_node.text)
    elif text_node.text_type == TextType.ORDERED_LIST:
        # I think this gets complicated because we need to use a li tag for ordered lists
        return LeafNode("li", text_node.text)
    elif text_node.text_type == TextType.BLOCKQUOTE:
        return LeafNode("blockquote", text_node.text)
    elif text_node.text_type == TextType.PARAGRAPH:
        return LeafNode("p", text_node.text)
    else:
        raise Exception("unknown text type")

def text_to_text_nodes(text):
    # split text by code, bold, and italic
    nodes = [TextNode(text, TextType.TEXT)]
    nodes = split_nodes_delimiter(nodes, "`", TextType.CODE)
    nodes = split_nodes_delimiter(nodes, "**", TextType.BOLD)
    nodes = split_nodes_delimiter(nodes, "_", TextType.ITALIC)
    nodes = split_nodes_image(nodes)
    nodes = split_nodes_link(nodes)
    return nodes

def markdown_to_blocks(markdown):
    # split the Markdown into blocks based on \n\n
    blocks = markdown.split("\n\n")
    # process each block
    processed_blocks = []
    for block in blocks:
        # split the block into lines
        if block == "":
            continue
        block = block.strip()
        processed_blocks.append(block)
    
    return processed_blocks

def block_to_block_type(block):
    if re.match(r"^#{1,6}", block):
        return BlockType.HEADING
    elif re.match(r"^`.+`$", block):
        return BlockType.CODE
    elif block.count("```") == 2:
        return BlockType.CODE_BLOCK
    elif re.match(r"^>.*", block):
        return BlockType.BLOCKQUOTE
    elif re.match(r"^[*+-] ", block):
        return BlockType.UNORDERED_LIST
    elif re.match(r"^\d+\.\s", block):
        return BlockType.ORDERED_LIST
    else:
        return BlockType.PARAGRAPH


def text_code_block_to_text_node(block):
    return TextNode(block, TextType.CODE_BLOCK)


def build_paragraph_children(block):
    paragraph_nodes = text_to_text_nodes(block)
    child_nodes = []
    for paragraph_node in paragraph_nodes:
        # I guess this is necessary because of how we split the text from the Markdown into paragraphs.
        paragraph_node.text = paragraph_node.text.replace("\n", " ")
        child_nodes.append(text_node_to_html_node(paragraph_node))
    return child_nodes


def build_list_node_children(block):
    blocks = block.split("\n")
    text_nodes = list(map(lambda x: text_to_text_nodes(x)[0], blocks))
    
    html_nodes = []
    for text_node in text_nodes:
        text_node.text = re.sub(r"([*+-]|\d{1,3}\.)\s*", "", text_node.text)
        if text_node.text_type == TextType.TEXT:
            # This is not a bug. It doesn't matter which list type we use since it will be up to the container to decide.
            text_node.text_type = TextType.UNORDERED_LIST
        html_nodes.append(text_node_to_html_node(text_node))
    return html_nodes

def build_block_quote_children(block):
    blocks = block.split("\n")
    text_nodes_lists = list(map(lambda x: text_to_text_nodes(x), blocks))
    
    html_nodes = []
    for inner_list in text_nodes_lists:
        for text_node in inner_list:
            if text_node.text_type == TextType.TEXT:
                text_node.text_type = TextType.PARAGRAPH
            text_node.text = re.sub(r"^>\s*", "", text_node.text)
            html_nodes.append(text_node_to_html_node(text_node))
        
    return html_nodes
        

def markdown_to_html_node(markdown):
    # make Markdown to blocks and then blocks to types and finally block types to HTML leaf nodes
    md_blocks = markdown_to_blocks(markdown)
    html_nodes = []
    for index in range(len(md_blocks)):
        block = md_blocks[index]
        block_type = block_to_block_type(block)
        if block_type == BlockType.HEADING:
            heading_node = text_to_text_nodes(block)[0]
            heading_node.text_type = TextType.HEADING
            html_nodes.append(text_node_to_html_node(heading_node))
        elif block_type == BlockType.CODE:
            code_node = text_to_text_nodes(block)[0]
            code_node.text_type = TextType.CODE
            html_nodes.append(text_node_to_html_node(code_node))
        elif block_type == BlockType.CODE_BLOCK:
            code_block_node = text_code_block_to_text_node(block)
            code_block_node.text_type = TextType.CODE
            html_nodes.append(code_block_to_code_parent_node(code_block_node))
        elif block_type == BlockType.QUOTE:
            quote_node = text_to_text_nodes(block)[0]
            quote_node.text_type = TextType.QUOTE
            html_nodes.append(text_node_to_html_node(quote_node))
        elif block_type == BlockType.UNORDERED_LIST:
            child_nodes = build_list_node_children(block)
            html_nodes.append(ParentNode("ul", child_nodes))
        elif block_type == BlockType.ORDERED_LIST:
            child_nodes = build_list_node_children(block)
            html_nodes.append(ParentNode("ol", child_nodes))
        elif block_type == BlockType.BLOCKQUOTE:
            child_nodes = build_block_quote_children(block)
            html_nodes.append(ParentNode("blockquote", child_nodes))       
        elif block_type == BlockType.PARAGRAPH:
            child_nodes = build_paragraph_children(block)
            html_nodes.append(ParentNode("p", child_nodes))            
            
    parent_node = ParentNode("div", html_nodes)
    return parent_node


def copy_static_to_public(src_dir, dst_dir):
    if not os.path.exists(dst_dir):
        os.mkdir(dst_dir)
        
    src_stuff = os.listdir(src_dir)
    for src_file in src_stuff:
        src_file_path = os.path.join(src_dir, src_file)
        if os.path.isdir(src_file_path):
            copy_static_to_public(src_file_path, os.path.join(dst_dir, src_file))
        else:
            shutil.copy(src_file_path, dst_dir)
        
            
            

def main():
    work_dir = os.getcwd()
    src_dir = os.path.join(work_dir, "static")
    dst_dir = os.path.join(work_dir, "public")
    shutil.rmtree(dst_dir, ignore_errors=True)
    copy_static_to_public(src_dir, dst_dir)

main()