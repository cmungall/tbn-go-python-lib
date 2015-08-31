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
        self.manager = p.parse("examples/ceph.owl")
        self.manager.load_prefix_map("examples/curies.yaml")
        logger.info("LOADED")
        return

    def tearDown(self):
        return

    def test_all(self):
        for c in self.manager.all_cls():
            show(c)

        self.assertTrue(False)

def show(c):
    if not c.label:
        return
    print("{:s} '{:s}'".format(c.id, c.label))
    for s in c.superclasses():
        print("  DIRECT SUPER: {:s} '{:s}'".format(s.id, s.label))
    for s in c.inferred_superclasses():
        print("  INFERRED SUPER: {:s} '{:s}'".format(s.id, s.label))


if __name__ == '__main__':
    unittest.main()
