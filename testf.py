#!/usr/bin/env python3

__author__ = 'nlw'

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
    mgr = p.parse("examples/mod.rdf")
    print(mgr)
    for i in mgr.all_individual():
        print("IND: {:s} '{:s}'".format(str(i), i.label("")))
        for f in i.facts_out():
            print("  FACT: {:s}".format(str(f)))


if __name__ == "__main__":
    main()


