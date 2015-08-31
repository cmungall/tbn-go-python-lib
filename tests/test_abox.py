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
        self.manager = p.parse("examples/mod.rdf")
        self.manager.load_prefix_map("examples/curies.yaml")
        logger.info("LOADED")
        return

    def tearDown(self):
        return

    def test_all(self):
        num_axiom_anns = 0
        for i in self.manager.all_individual():
            show(i)
            for f in i.facts_out():
                anns = f.annotations
                num_axiom_anns += len(anns)
        self.assertTrue(num_axiom_anns > 0)


def show(i):
    print("IND: {:s}".format(str(i)))
    for f in i.facts_out():
        anns = f.annotations
        print("  FACT: {:s} ANNS:{}".format(str(f), str(anns)))


if __name__ == '__main__':
    unittest.main()
