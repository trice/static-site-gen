import htmlnode
from htmlnode import HTMLNode

class LeafNode(HTMLNode):
    def __init__(self, tag, value, props=None):
        super().__init__(tag, value, None, props)

    def __tag_helper(self, tag, value, props):
        if props:
            return f"<{tag} {props}>{value}</{tag}>"
        else:
            return f"<{tag}>{value}</{tag}>"

    def to_html(self):
        if self.value == None:
            raise ValueError("value must be set")
        elif self.tag == None:
            return self.value
        else:
            match (self.tag):
                case "a" | "abbr":
                    return self.__tag_helper(self.tag, self.value, self.props_to_html())
                case "img":
                    return f"<img {self.props_to_html()}>"
                case "p" | "b" | "i" | "span" | "code" | "q" | "h1" | "h2" | "h3" | "h4" | "h5" | "h6" | "li":
                    return self.__tag_helper(self.tag, self.value, None)
                case _:
                    raise ValueError(f"unknow or unimplemented tag: {self.tag}")
