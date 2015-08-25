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
        logger.info("LOADED")
        return

    def tearDown(self):
        return

    def test_all(self):
        for c in self.manager.all_cls():
            print("{:s} '{:s}' DEF: '{:s}'".format(str(c), c.label(""), c.definition("")))
            for s in c.superclasses():
                logger.info("  SUPER: {:s} '{:s}'".format(str(s), s.label("")))
                for s in c.svf_superclasses(partOf):
                    logging.info("  PARTOF: {:s} '{:s}'".format(str(s), s.label("")))
        logging.info("Test query data finished.")
        self.assertTrue(False)



if __name__ == '__main__':
    unittest.main()
