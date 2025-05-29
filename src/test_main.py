import unittest
from main import text_node_to_html_node, split_nodes_delimiter, extract_markdown_links, extract_markdown_images, \
    TextNode, TextType, split_nodes_image, split_nodes_link, text_to_text_nodes, markdown_to_blocks


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
        result = split_nodes_delimiter([TextNode("This is a string with **bold** text and **some** more **bold text** and as an extra bonus even more **bold text**.", TextType.TEXT)], "**", TextType.BOLD)
        for index in range(len(result)):
            if index % 2 == 0:
                self.assertEqual(result[index].text_type, TextType.TEXT, f"Failed at index {index} contents: {result[index].text}")
            else:
                self.assertEqual(result[index].text_type, TextType.BOLD, f"Failed at index {index} contents: {result[index].text}")
    
    def test_split_nodes_delimiter_code_node(self):
        result = split_nodes_delimiter([TextNode("This is a string with `code` text and `some` more `code text` and as an extra bonus even more `code text`.", TextType.TEXT)], "`", TextType.CODE)
        for index in range(len(result)):
            if index % 2 == 0:
                self.assertEqual(result[index].text_type, TextType.TEXT, f"Failed at index {index} contents: {result[index].text}")
            else:
                self.assertEqual(result[index].text_type, TextType.CODE, f"Failed at index {index} contents: {result[index].text}")
        
    def test_split_nodes_delimiter_italics(self):
        result = split_nodes_delimiter([TextNode("This is a string with _italics_ text and _some_ more _italics text_ and as an extra bonus even more _italics text_.", TextType.TEXT)], "_", TextType.ITALIC)
        for index in range(len(result)):
            if index % 2 == 0:
                self.assertEqual(result[index].text_type, TextType.TEXT, f"Failed at index {index} contents: {result[index].text}")
            else:
                self.assertEqual(result[index].text_type, TextType.ITALIC, f"Failed at index {index} contents: {result[index].text}")
                
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
        new_nodes = text_to_text_nodes("This is **text** with an _italic_ word and a `code block` and an ![obi wan image](https://i.imgur.com/fJRm4Vk.jpeg) and a [link](https://boot.dev)")
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
    

if __name__ == "__main__":
    unittest.main()