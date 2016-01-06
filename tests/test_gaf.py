#!/usr/bin/env python3

import unittest
import logging

from legolib.parsers.AssociationParser import GAFParser
from legolib.render.NetworkExporter import NetworkExporter
import rdflib
from rdflib import Namespace
from networkx import write_yaml

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GAFTestCase(unittest.TestCase):
    def setUp(self):
        p = GAFParser()
        p.parse("examples/mgi50.gaf")
        self.parser = p
        return

    def tearDown(self):
        return

    def test_all(self):
        write_yaml(self.parser.merged_graph, 'target/gaf-graph.yaml')



if __name__ == '__main__':
    unittest.main()
