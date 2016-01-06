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

    def test_cls(self):
        id = "CEPH:0000308"
        app = self.manager.get_cls(id)
        show(app)
        sids = [s.id for s in app.inferred_superclasses()]
        print(sids)
        self.assertTrue(id in sids, "expected reflexivity")
        self.assertTrue("UBERON:0000026" in sids)
        self.assertTrue("UBERON:0000475" in sids)
        self.assertTrue("UBERON:0010000" in sids)
        sids = [s.id for s in app.inferred_subclasses()]
        self.assertTrue(id in sids, "expected reflexivity")
        self.assertTrue("CEPH:0000256" in sids)
        self.assertTrue("CEPH:0000015" in sids)
        self.assertTrue("CEPH:0000017" in sids, "expected transitivity")
        

    def test_all(self):
        for c in self.manager.all_cls():
            show(c)


def show(c):
    if not c.label:
        return
    print("{:s} '{:s}'".format(c.id, c.label))
    for s in c.superclasses():
        print("  DIRECT SUPER: {:s}".format(s.id))
        #print("  DIRECT SUPER: {:s} '{:s}'".format(s.id, str(s.label)))
    for s in c.inferred_superclasses():
        print("  INFERRED SUPER: {:s} '{:s}'".format(s.id, str(s.label)))


if __name__ == '__main__':
    unittest.main()
