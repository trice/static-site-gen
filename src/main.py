from textnode import TextType, TextNode
from leafnode import LeafNode


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
    delimiter_type_lookup = {"`": TextType.CODE, "**": TextType.BOLD, "_": TextType.ITALIC}

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
                    new_nodes.append(TextNode(chunks[index], delimiter_type_lookup[delimiter]))

    return new_nodes


def text_node_to_html_node(text_node):
    match text_node.text_type:
        case TextType.TEXT:
            return LeafNode(None, text_node.text)
        case TextType.BOLD:
            return LeafNode("b", text_node.text)
        case TextType.ITALIC:
            return LeafNode("i", text_node.text)
        case TextType.CODE:
            return LeafNode("code", text_node.text)
        case TextType.LINK:
            return LeafNode("a", text_node.text, props={"href": text_node.url})
        case TextType.IMAGE:
            return LeafNode("img", text_node.text, props={"src": text_node.url})
        case _:
            raise Exception("unknown text type")


def main():
    text_node = TextNode("This is some anchor text", TextType.LINK, "https://www.boot.dev")
    print(text_node)


main()
