__author__ = 'cjm'

import logging


class BasicReasoner:
    """
    Dumb structureal reasoner. Currently only subclass closure
    """

    def __init__(self, ontology=None):
        self.ontology = ontology

    # TODO: replace with something more efficient
    def inferred_superclasses(self,c):
        o = self.ontology
        stack = [c]
        ancs = []
        while len(stack) > 0:
            n = stack.pop()
            if not n in ancs:
                ancs.append(n)
                stack += n.superclasses()
        return ancs

    # TODO: replace with something more efficient
    def inferred_subclasses(self,c):
        o = self.ontology
        stack = c if isinstance(c,list) else [c]
        ancs = []
        while len(stack) > 0:
            n = stack.pop()
            if not n in ancs:
                ancs.append(n)
                stack += n.subclasses()
        return ancs
        
