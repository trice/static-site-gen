from functools import reduce

class HTMLNode:
    def __init__(self, tag=None, value=None, children=None, props=None):
        self.tag = tag
        self.value = value
        self.children = children
        self.props = props

    def to_html(self):
        raise NotImplementedError

    def join_props(self, kvp):
        return f"{kvp[0]}=\"{kvp[1]}\""

    def props_to_html(self):
        if self.props:
            return reduce(lambda paccum, pcurr: paccum + " " + pcurr, list(map(self.join_props, self.props.items()))) 
        else:
            return ""

    def __repr__(self):
        return f"HTMLNode({self.tag}, {self.value}, {self.children}, {self.props_to_html()})"
