import unittest
from main import text_node_to_html_node, TextNode, TextType


class TestMain(unittest.TestCase):
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

if __name__ == "__main__":
    unittest.main()