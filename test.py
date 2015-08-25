#!/usr/bin/env python3

__author__ = 'cjm'

import argparse
import logging
import unittest

from legolib.rdf.OWLParser import OWLParser

import rdflib
from rdflib import Namespace
from rdflib.namespace import RDF
from rdflib.namespace import SKOS

RO = Namespace('http://purl.obolibrary.org/obo/RO_')
BFO = Namespace('http://purl.obolibrary.org/obo/BFO_')
OBO = Namespace('http://purl.obolibrary.org/obo/')

partOf = OBO.BFO_0000050

def main():
    print("Welcome:")
    p = OWLParser()
    mgr = p.parse("examples/ceph.owl")
    mgr.load_prefix_map("examples/curies.yaml")
    print(mgr)
    for p in mgr.all_property():
        print("{:s} '{:s}' TR: '{:b}'".format(p.id, p.label(""), p.is_transitive))
    for c in mgr.all_cls():
        print("{:s} '{:s}' DEF: '{:s}'".format(c.id, c.label(""), c.definition("")))
        for s in c.exactSynonyms():
            print("  AKA: {:s}".format(s))
        for s in c.superclasses():
            print("  SUPER: {:s} '{:s}'".format(s.id, s.label("")))
        for s in c.svf_superclasses(partOf):
            print("  PARTOF: {:s} '{:s}'".format(str(s), s.label("")))


if __name__ == "__main__":
    main()


