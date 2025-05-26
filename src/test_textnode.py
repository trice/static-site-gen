import unittest

from textnode import TextNode, TextType


class TestTextNode(unittest.TestCase):
    def test_eq(self):
        node = TextNode("This is a text node", TextType.BOLD)
        node2 = TextNode("This is a text node", TextType.BOLD)
        self.assertEqual(node, node2)

    def test_neq(self):
        node = TextNode("This is a text node", TextType.LINK)
        node2 = TextNode("This is a text node", TextType.BOLD)
        self.assertNotEqual(node, node2)

    def test_urlNone(self):
        node = TextNode("This is just a test", TextType.LINK, None)
        node2 = TextNode("This is just a test", TextType.LINK, None)
        self.assertEqual(node, node2)

    def test_urlSet(self):
        expected = "http://localhost:1122"
        node = TextNode("This is just a test", TextType.LINK, expected)
        self.assertEqual(expected, node.url)

if __name__ == "__main__":
    unittest.main()

