import re

from leafnode import LeafNode
from textnode import TextType, TextNode


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
    Splits the text of nodes containing Markdown links into separate nodes, while maintaining 
    the structure of the original content. Each Markdown link in a text is isolated, and the 
    resulting split content is used to create a series of nodes, distinguished as plain text 
    or link types.

    :param old_nodes: A list of nodes, where each node is expected to contain text that 
                      may or may not include Markdown links.
    :type old_nodes: list[TextNode]
    :return: A list of newly created nodes where Markdown links in the text have been 
             split into individual link nodes, and other text is represented as text nodes.
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


def text_node_to_html_node(text_node):
    """
    Converts a `text_node` object into an appropriate HTML node representation based on 
    the type of text it contains. This function maps specific text types such as plain 
    text, bold, italic, code, link, and images to their corresponding HTML elements.

    :param text_node: The input object contains information about the text and its type.
                      It must include attributes such as `text_type`, `text`, and for 
                      certain types, `url`.

    :return: An instance of `LeafNode` representing the equivalent HTML node for the 
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
    elif text_node.text_type == TextType.LINK:
        return LeafNode("a", text_node.text, props={"href": text_node.url})
    elif text_node.text_type == TextType.IMAGE:
        return LeafNode("img", text_node.text, props={"src": text_node.url})
    else:
        raise Exception("unknown text type")

def text_to_text_nodes(text):
    # split text by code, bold, and italic
    code_nodes = split_nodes_delimiter([TextNode(text, TextType.TEXT)], "`", TextType.CODE)
    bold_nodes = split_nodes_delimiter(code_nodes, "**", TextType.BOLD)
    italic_nodes = split_nodes_delimiter(bold_nodes, "_", TextType.ITALIC)
    image_nodes = split_nodes_image(italic_nodes)
    link_nodes = split_nodes_link(image_nodes)
    return link_nodes

def main():
    text_node = TextNode("This is some anchor text", TextType.LINK, "https://www.boot.dev")
    print(text_node)


main()