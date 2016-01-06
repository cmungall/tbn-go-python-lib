#!/usr/bin/env python3

import unittest
import logging

from legolib.rdf.OWLParser import OWLParser
from legolib.render.NetworkExporter import NetworkExporter
import rdflib
from rdflib import Namespace

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
        x = NetworkExporter(self.manager)
        x.export_yaml('target/model.yaml')



if __name__ == '__main__':
    unittest.main()
