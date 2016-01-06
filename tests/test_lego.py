#!/usr/bin/env python3

import unittest
import logging

from legolib.rdf.OWLParser import OWLParser
from legolib.model.Lego import Model

import rdflib
from rdflib import Namespace

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OntologyTestCase(unittest.TestCase):
    def setUp(self):
        p = OWLParser()
        self.manager = p.parse("examples/mod.rdf")
        self.manager.load_prefix_map("examples/curies.yaml")
        self.model = Model(self.manager)
        return

    def tearDown(self):
        return

    def test_all(self):
        num_axrefs = 0
        nk = 0
        for a in self.model.all_activity:
            show(a)
        for a in self.model.all_evidence:
            show_evidence(a)


def show(i):
    print("ACT: {:s}".format(str(i)))
    for a in i.location_assertions:
        print("  LOCATION: {:s} E: {:s}".format(jstr(a.location_types), jstr(a.all_evidence)))
    for a in i.enabled_by_assertions:
        print("  ENABLED_BY: {:s} E: {:s}".format(jstr(a.molecule_types), jstr(a.all_evidence)))
    for a in i.causal_assertions:
        print("  AFFECTS: {:d} {:s} {:s} E: {:s}".format(a.direction, str(a.is_controlling), str(a.affects), jstr(a.all_evidence)))


def show_evidence(e):
    print("EV: {:s}".format(str(e)))


def jstr(l):
    if not isinstance(l, list):
        return str(l)+"?"
    else:
        return format(", ".join(map(str, l)))

if __name__ == '__main__':
    unittest.main()
