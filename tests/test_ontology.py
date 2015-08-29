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

        # Test fetch using complete URI
        tc = self.manager.get_cls("http://purl.obolibrary.org/obo/CEPH_0000291")
        self.assertTrue(tc.label == 'tentacular club', "expected label of "+str(tc)+" to be tentacular club, instead was " + str(tc.label))

        # Test fetch using CURIE
        tc = self.manager.get_cls("CEPH:0000291")
        show(tc)
        self.assertTrue(tc.label == 'tentacular club', "expected label of "+str(tc)+" to be tentacular club, instead was " + str(tc.label))

        # Test definition
        tc = self.manager.get_cls("CEPH:0000171")
        show(tc)
        self.assertTrue(tc.definition.startswith('In males, the large storage sac for spermatophores that is an expanded region of the genital duct'))

        # Test syns
        tc = self.manager.get_cls("CEPH:0000054")
        show(tc)
        self.assertTrue('proximal locking-apparatus' in tc.synonyms, "Expected PLA in syns, instead got: "+",".join(tc.synonyms))

        # Test logical axioms
        tc = self.manager.get_cls("CEPH:0000296")
        show(tc)
        sc = self.manager.get_cls("UBERON:0000477")
        self.assertTrue(sc in tc.superclasses(), "Expected 'anatomical cluster' to be in superclasses of subesophageal mass")

        # Test logical axioms
        tc = self.manager.get_cls("CEPH:0000291")
        show(tc)
        pc = self.manager.get_cls("CEPH:0000256")
        self.assertTrue(pc in tc.svf_superclasses(partOf), "Expected 'tentacle' to be in part-of existential parent")
        
        logging.info("Test query data finished.")
        self.assertTrue(True)

def show(c):
    if not c.label:
        return
    if c.definition:
        print("{:s} '{:s}' DEF: '{:s}'".format(c.id, c.label, c.definition))
    else:
        print("{:s} '{:s}'".format(c.id, c.label))
    for s in c.synonyms:
        print("  AKA: {:s}".format(s))
    for s in c.superclasses():
        print("  SUPER: {:s} '{:s}'".format(s.id, s.label))
    for s in c.svf_superclasses(partOf):
        print("  PARTOF: {:s} '{:s}'".format(str(s), s.label))


if __name__ == '__main__':
    unittest.main()
