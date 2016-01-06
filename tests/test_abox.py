#!/usr/bin/env python3


import unittest
import logging

from legolib.rdf.OWLParser import OWLParser
from legolib.model.Ontology import annotations_to_dict

import rdflib
from rdflib import Namespace

OBO = Namespace('http://purl.obolibrary.org/obo/')

partOf = OBO.BFO_0000050
occursIn = OBO.BFO_0000066
enabledBy = OBO.RO_0002333

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

    def test_node(self):
        id = "GOMODEL:539a033300000004/539a03330000005"
        m = self.manager
        ind = m.get_individual(id)
        show(ind)
        facts = ind.facts_out()
        self.assertTrue(len(facts)==3)
        facts = ind.facts_out(occursIn)
        self.assertTrue(len(facts)==1)
        f = facts[0]
        self.assertTrue(len(f.annotations)==1)
        facts = ind.facts_out(enabledBy)
        self.assertTrue(len(facts)==1)
        f = facts[0]
        self.assertTrue(len(f.annotations)==1)

    def test_all(self):
        num_axrefs = 0
        nk = 0
        for i in self.manager.all_individual():
            show(i)
            for f in i.facts_out():
                axrefs = f.axiomrefs
                num_axrefs += len(axrefs)
                anns = f.annotations
                if len(anns) > 0:
                    dict = annotations_to_dict(anns)
                    print(str(dict))
                    nk += len(dict.keys())
        self.assertTrue(num_axrefs > 0)
        self.assertTrue(nk > 0)


def show(i):
    print("IND: {:s}".format(str(i)))
    for f in i.facts_out():
        anns = f.annotations
        print("  FACT: {:s} ANNS:{}".format(str(f), "; ".join(map(str, anns))))


if __name__ == '__main__':
    unittest.main()
