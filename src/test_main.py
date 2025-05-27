import unittest
from main import text_node_to_html_node, split_nodes_delimiter, TextNode, TextType


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
        
    def test_code_tohtml(self):
        node = TextNode("This is a CODE node", TextType.CODE)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.to_html(), "<code>This is a CODE node</code>")
        
    def test_image_tohtml(self):
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
        result = split_nodes_delimiter([TextNode("This is a string with **bold** text and **some** more **bold text** and as an extra bonus even more **bold text**.", TextType.TEXT)], "**", TextType.TEXT)
        for index in range(len(result)):
            if index % 2 == 0:
                self.assertEqual(result[index].text_type, TextType.TEXT, f"Failed at index {index} contents: {result[index].text}")
            else:
                self.assertEqual(result[index].text_type, TextType.BOLD, f"Failed at index {index} contents: {result[index].text}")
    
    def test_split_nodes_delimiter_code_node(self):
        result = split_nodes_delimiter([TextNode("This is a string with `code` text and `some` more `code text` and as an extra bonus even more `code text`.", TextType.TEXT)], "`", TextType.TEXT)
        for index in range(len(result)):
            if index % 2 == 0:
                self.assertEqual(result[index].text_type, TextType.TEXT, f"Failed at index {index} contents: {result[index].text}")
            else:
                self.assertEqual(result[index].text_type, TextType.CODE, f"Failed at index {index} contents: {result[index].text}")
        
    def test_split_nodes_delimiter_italics(self):
        result = split_nodes_delimiter([TextNode("This is a string with _italics_ text and _some_ more _italics text_ and as an extra bonus even more _italics text_.", TextType.TEXT)], "_", TextType.TEXT)
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
        
if __name__ == "__main__":
    unittest.main()