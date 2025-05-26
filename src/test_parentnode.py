import unittest

from leafnode import LeafNode
from parentnode import ParentNode


class TestLeafNode(unittest.TestCase):
    def test_parent_child_p(self):
        parent_node = ParentNode("p",
                                 [
                                     LeafNode("b", "This is a test"),
                                     LeafNode("abbr", "US", props={"title": "United States"}),
                                     ParentNode("p", [
                                         LeafNode("b", "of America"),
                                         LeafNode("a", "Here we go", props={"href": "http://localhost:8080"}),                                         
                                     ])
                                 ])
        result = parent_node.to_html()
        expected = "<p><b>This is a test</b><abbr title=\"United States\">US</abbr><p><b>of America</b><a href=\"http://localhost:8080\">Here we go</a></p></p>"
        self.assertEqual(result, expected)

    def test_to_html_with_children(self):
        child_node = LeafNode("span", "child")
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(parent_node.to_html(), "<div><span>child</span></div>")

    def test_to_html_with_grandchildren(self):
        grandchild_node = LeafNode("b", "grandchild")
        child_node = ParentNode("span", [grandchild_node])
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(
            parent_node.to_html(),
            "<div><span><b>grandchild</b></span></div>",
        )

if __name__ == "__main__":
    unittest.main()
