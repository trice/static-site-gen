from functools import reduce
import htmlnode
from htmlnode import HTMLNode

class ParentNode(HTMLNode):
    def __init__(self, tag, children, props=None):
        super().__init__(tag, None, children, props)

    def __child_reducer(self, children):
        return reduce(lambda a, b: a + b, map(lambda x: x.to_html(), children))

    def __tag_helper(self, tag, children):
        return f"<{tag}>{self.__child_reducer(children)}</{tag}>"

    def to_html(self):
        if not self.tag:
            raise ValueError("tag is a required parameter")
        elif not self.children:
            raise ValueError("children is a required parameter")
        else:
            match(self.tag):
                case "p" | "div" | "span":
                    return self.__tag_helper(self.tag, self.children)

