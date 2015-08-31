#!/usr/bin/env python3

import unittest
import logging

from legolib.rdf.OWLParser import OWLParser
from legolib.render.NetworkExporter import NetworkExporter
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
        x = NetworkExporter(self.manager)
        x.export_yaml('target/foo.yaml')



if __name__ == '__main__':
    unittest.main()
