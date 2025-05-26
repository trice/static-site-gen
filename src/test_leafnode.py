import unittest

import leafnode
from leafnode import LeafNode

class TestLeafNode(unittest.TestCase):
    def test_leaf_to_html_p(self):
        node = LeafNode("p", "Hello, world!")
        self.assertEqual(node.to_html(), "<p>Hello, world!</p>")

    def test_leaf_to_html_a(self):
        node = LeafNode("a", "Hello, world!", props={"href":"http://localhost:8080"})
        self.assertEqual(node.to_html(), "<a href=\"http://localhost:8080\">Hello, world!</a>")

    def test_leaf_to_html_unknown(self):
        node = LeafNode("g", "Hi there!")
        with self.assertRaises(ValueError):
            node.to_html()

    def test_leaf_to_html_tag_none(self):
        node = LeafNode(None, "Hi there!")
        self.assertEqual(node.to_html(), "Hi there!")

    def test_leaf_to_html_b(self):
        node = LeafNode("b", "I have the power!!")
        self.assertEqual(node.to_html(), "<b>I have the power!!</b>")

    def test_leaf_to_html_abbr(self):
        node = LeafNode("abbr", "USSR", props={"title":"Union of Soviet Socialists Republic"})
        self.assertEqual(node.to_html(), "<abbr title=\"Union of Soviet Socialists Republic\">USSR</abbr>")
