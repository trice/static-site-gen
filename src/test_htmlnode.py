import unittest
from htmlnode import HTMLNode

class TestHTMLNode(unittest.TestCase):
    def test_None(self):
        html_node = HTMLNode();
        self.assertEqual(repr(html_node), "HTMLNode(None, None, None, None)")

    def test_no_props_no_children(self):
        html_node = HTMLNode("h1", "I am the egg man", None, None)
        self.assertEqual(repr(html_node), "HTMLNode(h1, I am the egg man, None, None)")

    def test_to_html_raises_exception(self):
        html_node = HTMLNode()
        with self.assertRaises(NotImplementedError):
            html_node.to_html()

    def test_props_to_html_expecting_string(self):
        html_node = HTMLNode(props={"href":"http://localhost:8080","target":"blank_"})
        result = html_node.props_to_html()
        expected = "href=\"http://localhost:8080\" target=\"blank_\""
        self.assertEqual(result, expected)



if __name__ == "__main__":
    unittest.main()

