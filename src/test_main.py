import unittest
from unittest import TestCase

from main import text_node_to_html_node, split_nodes_delimiter, extract_markdown_links, extract_markdown_images, \
    TextNode, TextType, split_nodes_image, split_nodes_link, text_to_text_nodes, markdown_to_blocks, \
    block_to_block_type, BlockType, heading_text_to_heading_leafnode, markdown_to_html_node


class TestMainTextNodeToHtmlNode(unittest.TestCase):
    def test_text(self):
        node = TextNode("This is a text node", TextType.TEXT)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, None)
        self.assertEqual(html_node.value, "This is a text node")

    def test_bold(self):
        node = TextNode("This is a BOLD node", TextType.BOLD)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "b")
        self.assertEqual(html_node.value, "This is a BOLD node")

    def test_link(self):
        node = TextNode("This is a LINK node", TextType.LINK, "http://localhost:8080")
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "a")
        self.assertEqual(html_node.props["href"], "http://localhost:8080")
        self.assertEqual(html_node.value, "This is a LINK node")

    def test_italic(self):
        node = TextNode("This is a ITALIC node", TextType.ITALIC)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "i")
        self.assertEqual(html_node.value, "This is a ITALIC node")

    def test_image(self):
        node = TextNode("This is a IMAGE node", TextType.IMAGE, "http://localhost:8080/image.png")
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "img")
        self.assertEqual(html_node.props["src"], "http://localhost:8080/image.png")
        self.assertEqual(html_node.value, "This is a IMAGE node")

    def test_code(self):
        node = TextNode("This is a CODE node", TextType.CODE)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "code")
        self.assertEqual(html_node.value, "This is a CODE node")

    def test_code_to_html(self):
        node = TextNode("This is a CODE node", TextType.CODE)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.to_html(), "<code>This is a CODE node</code>")

    def test_image_to_html(self):
        node = TextNode("This is a IMAGE node", TextType.IMAGE, "http://localhost:8080/image.png")
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.to_html(), "<img src=\"http://localhost:8080/image.png\">")


class TestMainSplitNodesDelimiter(unittest.TestCase):
    def test_split_nodes_delimiter(self):
        with self.assertRaises(ValueError):
            split_nodes_delimiter([], "!", TextType.TEXT)

    def test_split_nodes_delimiter_empty(self):
        with self.assertRaises(ValueError):
            split_nodes_delimiter([], "", TextType.TEXT)

    def test_split_nodes_delimiter_non_TEXT(self):
        result = split_nodes_delimiter([TextNode("Hello", TextType.BOLD)], "**", TextType.BOLD)
        self.assertEqual(result, [TextNode("Hello", TextType.BOLD)])

    def test_split_nodes_delimiter_one_node(self):
        result = split_nodes_delimiter([TextNode(
            "This is a string with **bold** text and **some** more **bold text** and as an extra bonus even more **bold text**.",
            TextType.TEXT)], "**", TextType.BOLD)
        for index in range(len(result)):
            if index % 2 == 0:
                self.assertEqual(result[index].text_type, TextType.TEXT,
                                 f"Failed at index {index} contents: {result[index].text}")
            else:
                self.assertEqual(result[index].text_type, TextType.BOLD,
                                 f"Failed at index {index} contents: {result[index].text}")

    def test_split_nodes_delimiter_code_node(self):
        result = split_nodes_delimiter([TextNode(
            "This is a string with `code` text and `some` more `code text` and as an extra bonus even more `code text`.",
            TextType.TEXT)], "`", TextType.CODE)
        for index in range(len(result)):
            if index % 2 == 0:
                self.assertEqual(result[index].text_type, TextType.TEXT,
                                 f"Failed at index {index} contents: {result[index].text}")
            else:
                self.assertEqual(result[index].text_type, TextType.CODE,
                                 f"Failed at index {index} contents: {result[index].text}")

    def test_split_nodes_delimiter_italics(self):
        result = split_nodes_delimiter([TextNode(
            "This is a string with _italics_ text and _some_ more _italics text_ and as an extra bonus even more _italics text_.",
            TextType.TEXT)], "_", TextType.ITALIC)
        for index in range(len(result)):
            if index % 2 == 0:
                self.assertEqual(result[index].text_type, TextType.TEXT,
                                 f"Failed at index {index} contents: {result[index].text}")
            else:
                self.assertEqual(result[index].text_type, TextType.ITALIC,
                                 f"Failed at index {index} contents: {result[index].text}")

    def test_split_nodes_delimiter_check_for_pair(self):
        with self.assertRaises(Exception):
            split_nodes_delimiter([TextNode("This is **busted.", TextType.TEXT)], "**", TextType.TEXT)

    def test_split_nodes_delimiter_check_for_pair_code(self):
        with self.assertRaises(Exception):
            split_nodes_delimiter([TextNode("This is `busted.", TextType.TEXT)], "`", TextType.TEXT)

    def test_split_nodes_delimiter_check_for_pair_italics(self):
        with self.assertRaises(Exception):
            split_nodes_delimiter([TextNode("This is _busted.", TextType.TEXT)], "_", TextType.TEXT)

    def test_split_nodes_delimiter_check_for_no_delimiters_bold(self):
        """
        Test if the delimiter check does not throw an exception for plain old strings without the delimiter.
        """
        result = split_nodes_delimiter([TextNode("This is a string", TextType.TEXT)], "**", TextType.TEXT)
        self.assertEqual(result, [TextNode("This is a string", TextType.TEXT)])


class TestMainImageAndLinkExtract(unittest.TestCase):
    def test_extract_markdown_images(self):
        matches = extract_markdown_images(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png)"
        )
        self.assertListEqual([("image", "https://i.imgur.com/zjjcJKZ.png")], matches)

    def test_extract_markdown_links(self):
        matches = extract_markdown_links(
            "This is text with a [link](https://www.google.com)"
        )
        self.assertListEqual([("link", "https://www.google.com")], matches)

    def test_split_images(self):
        node = TextNode(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png) and another ![second image](https://i.imgur.com/3elNhQu.png)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [
                TextNode("This is text with an ", TextType.TEXT),
                TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png"),
                TextNode(" and another ", TextType.TEXT),
                TextNode(
                    "second image", TextType.IMAGE, "https://i.imgur.com/3elNhQu.png"
                ),
            ],
            new_nodes,
        )

    def test_split_links(self):
        node = TextNode(
            "This is text with a [link](https://www.google.com) and another [second link](https://www.google.com)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_link([node])
        self.assertListEqual(
            [
                TextNode("This is text with a ", TextType.TEXT),
                TextNode("link", TextType.LINK, "https://www.google.com"),
                TextNode(" and another ", TextType.TEXT),
                TextNode("second link", TextType.LINK, "https://www.google.com")
            ],
            new_nodes
        )


class TestMainMarkdownToNodes(unittest.TestCase):
    def test_markdown_to_text_nodes(self):
        new_nodes = text_to_text_nodes(
            "This is **text** with an _italic_ word and a `code block` and an ![obi wan image](https://i.imgur.com/fJRm4Vk.jpeg) and a [link](https://boot.dev)")
        expected_nodes = [
            TextNode("This is ", TextType.TEXT),
            TextNode("text", TextType.BOLD),
            TextNode(" with an ", TextType.TEXT),
            TextNode("italic", TextType.ITALIC),
            TextNode(" word and a ", TextType.TEXT),
            TextNode("code block", TextType.CODE),
            TextNode(" and an ", TextType.TEXT),
            TextNode("obi wan image", TextType.IMAGE, "https://i.imgur.com/fJRm4Vk.jpeg"),
            TextNode(" and a ", TextType.TEXT),
            TextNode("link", TextType.LINK, "https://boot.dev"),
        ]
        self.assertListEqual(expected_nodes, new_nodes)


class TestMainMarkdownBlocks(unittest.TestCase):
    def test_markdown_to_blocks(self):
        md = """
This is **bolded** paragraph

This is another paragraph with _italic_ text and `code` here
This is the same paragraph on a new line

- This is a list
- with items
"""
        blocks = markdown_to_blocks(md)
        self.assertEqual(
            blocks,
            [
                "This is **bolded** paragraph",
                "This is another paragraph with _italic_ text and `code` here\nThis is the same paragraph on a new line",
                "- This is a list\n- with items",
            ],
        )

    def test_block_to_block_type(self):
        md = """
This is **bolded** paragraph

This is another paragraph with _italic_ text and `code` here
This is the same paragraph on a new line

- This is a list
- with items

```print("Hello, world!")```

> This is a quote block.

+ This is a unordered list.

1. This is a numbered list.
2. This is another numbered list.

# heading 1

## heading 2

### heading 3

#### heading 4

##### heading 5

###### heading 6

"""
        blocks = markdown_to_blocks(md) 
        
        batch_results = []
        for block in blocks:
            result = block_to_block_type(block)
            batch_results.append(result)
        
        self.assertEqual(
            batch_results,
            [
                BlockType.PARAGRAPH,
                BlockType.PARAGRAPH,
                BlockType.UNORDERED_LIST,
                BlockType.CODE,
                BlockType.QUOTE,
                BlockType.UNORDERED_LIST,
                BlockType.ORDERED_LIST,
                BlockType.HEADING,
                BlockType.HEADING,
                BlockType.HEADING,
                BlockType.HEADING,
                BlockType.HEADING,
                BlockType.HEADING
            ],
        )
    
    def test_text_node_to_heading1_leaf_node(self):
        node = TextNode("# This is a heading", TextType.HEADING)
        html_node = heading_text_to_heading_leafnode(node)
        self.assertEqual(html_node.tag, "h1")
        self.assertEqual(html_node.value, "This is a heading")
    
    def test_text_node_to_heading2_leaf_node(self):
        node = TextNode("## This is a heading", TextType.HEADING)
        html_node = heading_text_to_heading_leafnode(node)
        self.assertEqual(html_node.tag, "h2")
        self.assertEqual(html_node.value, "This is a heading")
        
    def test_text_node_to_heading3_leaf_node(self):
        node = TextNode("### This is a heading", TextType.HEADING)
        html_node = heading_text_to_heading_leafnode(node)
        self.assertEqual(html_node.tag, "h3")
        self.assertEqual(html_node.value, "This is a heading")
        
    def test_text_node_to_heading4_leaf_node(self):
        node = TextNode("#### This is a heading", TextType.HEADING)
        html_node = heading_text_to_heading_leafnode(node)
        self.assertEqual(html_node.tag, "h4")
        self.assertEqual(html_node.value, "This is a heading")
        
    def test_text_node_to_heading5_leaf_node(self):
        node = TextNode("##### This is a heading", TextType.HEADING)
        html_node = heading_text_to_heading_leafnode(node)
        self.assertEqual(html_node.tag, "h5")
        self.assertEqual(html_node.value, "This is a heading")
        
    def test_text_node_to_heading6_leaf_node(self):
        node = TextNode("###### This is a heading", TextType.HEADING)
        html_node = heading_text_to_heading_leafnode(node)
        self.assertEqual(html_node.tag, "h6")
        self.assertEqual(html_node.value, "This is a heading")
        
    def test_text_node_to_heading7_leaf_node(self):
        node = TextNode("####### This is a heading", TextType.HEADING)
        with self.assertRaises(Exception):
            heading_text_to_heading_leafnode(node)
            
    def test_markdown_nodes_to_html_nodes_expecting_heading1(self):
        md = """
# heading 1
        """
        leaf_nodes = markdown_to_html_node(md)
        html = leaf_nodes.to_html()
        self.assertEqual(html, "<div><h1>heading 1</h1></div>")
        
    def test_markdown_nodes_to_html_nodes_expecting_code(self):
        md = """
```
print("Hello, world!")
print("this is a code block")        
```
        """
        leaf_node = markdown_to_html_node(md)
        html = leaf_node.to_html()
        self.assertEqual(html, "<div><pre><code>print(\"Hello, world!\")\nprint(\"this is a code block\")</code></pre></div>")


    def test_paragraphs(self):
        md = """
This is **bolded** paragraph
text in a p
tag here

This is another paragraph with _italic_ text and `code` here
    """
    
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><p>This is <b>bolded</b> paragraph text in a p tag here</p><p>This is another paragraph with <i>italic</i> text and <code>code</code> here</p></div>",
        )
    
    def test_codeblock(self):
        md = """
```
This is text that _should_ remain
the **same** even with inline stuff
```
    """
    
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><pre><code>This is text that _should_ remain\nthe **same** even with inline stuff</code></pre></div>",
        )
        
#     def test_block_quote(self):
#         md = """
# > The quarterly results look great!
# >
# > Revenue was off the chart.
# > Profits were higher than ever.
# >
# > _Everything_ is going according to **plan**.
#         """
#         node = markdown_to_html_node(md)
#         html = node.to_html()
#         self.assertEqual(html, "<div><blockquote><p>The quarterly results look great!</p><p></p><p>Revenue was off the chart.</p><p>Profits were higher than ever.</p><p></p><p><i>Everything</i> is going according to <b>plan</b>.</p></blockquote></div>")

if __name__ == "__main__":
    unittest.main()


