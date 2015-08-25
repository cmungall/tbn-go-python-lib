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

owlparser = OWLParser()

def main():

    parser = argparse.ArgumentParser(description='Lego'
                                                 'Client lib for Lego',
                                     formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument('-t', '--to', type=str, required=False,
                        help='Renderer')
    parser.add_argument('-p', '--prefixes', type=str, required=False,
                        help='Prefix map file')


    subparsers = parser.add_subparsers(dest='subcommand', help='sub-command help')
    
    # SUBCOMMAND
    parser_n = subparsers.add_parser('ac', help='all_class')
    parser_n.set_defaults(function=list_all_cls)
    parser_n.add_argument('files',nargs='*')

    parser_n = subparsers.add_parser('ai', help='all_individual')
    parser_n.set_defaults(function=list_all_individual)
    parser_n.add_argument('files',nargs='*')

    args = parser.parse_args()

    ## PROCESS GLOBALS

    mgr = owlparser.parse(args.files[0]) ## TODO
    if args.prefixes:
        mgr.load_prefix_map(args.prefixes)

    func = args.function
    func(mgr, args)


def list_all_cls(mgr, args):
    for c in mgr.all_cls():
        print(str(c))
        if c.definition:
            print(' DEF: "{:s}"'.format(c.definition))
        for s in c.exactSynonyms():
            print("  AKA: {:s}".format(s))
        for s in c.superclasses():
            print("  SUPER: {:s} '{:s}'".format(s.id, s.label))
        for s in c.svf_superclasses(partOf):
            print("  PARTOF: {:s} '{:s}'".format(str(s), s.label))
        for (p,fillers) in c.svf_superclass_map().items():
            for filler in fillers:
                print("    {:s} {:s}".format(str(p), str(filler)))

def list_all_individual(mgr, args):
    for i in mgr.all_individual():
        print(str(i))
        for f in i.facts_out():
            print("  FACT: {:s}".format(str(f)))


if __name__ == "__main__":
    main()
    
