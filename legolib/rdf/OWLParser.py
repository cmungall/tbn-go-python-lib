__author__ = 'cjm'

import logging

import rdflib
from rdflib import Namespace
from rdflib.namespace import RDF
from rdflib.namespace import RDFS
from rdflib.namespace import OWL

from legolib.model.Ontology import *

class OWLParser:

    def __init__(self, obj={}):    
        self.g = rdflib.Graph()
        self.manager = OntologyManager()

    def parse(self, f):
        self.g.parse(f)
        self.manager = OntologyManager(self.g)
        return self.manager


        

        
