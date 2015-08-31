#!/usr/bin/env python3


import unittest
import logging

from legolib.rdf.OWLParser import OWLParser
import rdflib
from rdflib import Namespace

OBO = Namespace('http://purl.obolibrary.org/obo/')

partOf = OBO.BFO_0000050

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OntologyTestCase(unittest.TestCase):
    def setUp(self):
        p = OWLParser()
        self.manager = p.parse("examples/ro.rdf")
        self.manager.load_prefix_map("examples/curies.yaml")
        logger.info("LOADED")
        return

    def tearDown(self):
        return

    def test_all(self):
        for i in self.manager.all_property():
            show(i)
        self.assertTrue(True)


def show(p):
    if not p.label:
        return
    if p.definition:
        print("{:s} '{:s}' DEF: '{:s}'".format(p.id, p.label, p.definition))
    else:
        print("{:s} '{:s}'".format(p.id, p.label))
    if p.is_transitive:
        print("TRANSITIVE")
    for s in p.synonyms:
        print("  AKA: {:s}".format(s))
    for s in p.superproperties():
        if not s.is_top:
            if s.label is None:
                print("  SUPER: {:s} NO LABEL".format(s.id))
            else:
                print("  SUPER: {:s} '{:s}'".format(s.id, s.label))


if __name__ == '__main__':
    unittest.main()
