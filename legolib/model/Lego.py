"""

This module provides a way of interacting with LEGO models: instantiations of GO classes connected using RO relations.

The objects here are lightweight delegators to Ontology individuals and facts (which are themselves backed by RDF graphs)

"""

__author__ = 'cjm'

import logging

from rdflib import Namespace
from rdflib import BNode
from rdflib import Literal
from rdflib import URIRef

OBO = Namespace('http://purl.obolibrary.org/obo/')
LEGO = Namespace('http://geneontology.org/lego/')

OCCURS_IN = OBO.BFO_0000066
ENABLED_BY = OBO.RO_0002333

CAUSALLY_UPSTREAM_OF_OR_WITHIN = OBO.RO_0002418
REGULATES_IN_OTHER_ORGANISM = OBO.RO_0002010
REGULATES = OBO.RO_0002211
NEGATIVELY_REGULATES = OBO.RO_0002212
DIRECTLY_INHIBITS = OBO.RO_0002408
INDIRECTLY_INHIBITS = OBO.RO_0002409
POSITIVELY_REGULATES = OBO.RO_0002213
DIRECTLY_ACTIVATES = OBO.RO_0002406
INDIRECTLY_ACTIVATES = OBO.RO_0002407
DIRECTLY_REGULATES = OBO.RO_0002578
CAUSALLY_UPSTREAM_OF = OBO.RO_0002411
IMMEDIATELY_CAUSALLY_UPSTREAM_OF = OBO.RO_0002412
DIRECTLY_PROVIDES_INPUT_FOR = OBO.RO_0002413
DIRECTLY_REGULATES = OBO.RO_0002578
TRANSITIVELY_PROVIDES_INPUT_FOR = OBO.RO_0002414
DIRECTLY_PROVIDES_INPUT_FOR = OBO.RO_0002413

CAUSAL_RELATIONS = [CAUSALLY_UPSTREAM_OF_OR_WITHIN, REGULATES_IN_OTHER_ORGANISM, REGULATES, NEGATIVELY_REGULATES, DIRECTLY_INHIBITS, INDIRECTLY_INHIBITS, POSITIVELY_REGULATES, DIRECTLY_ACTIVATES, INDIRECTLY_ACTIVATES, DIRECTLY_REGULATES, DIRECTLY_ACTIVATES, DIRECTLY_INHIBITS, CAUSALLY_UPSTREAM_OF, IMMEDIATELY_CAUSALLY_UPSTREAM_OF, DIRECTLY_ACTIVATES, DIRECTLY_INHIBITS, DIRECTLY_PROVIDES_INPUT_FOR, DIRECTLY_REGULATES, DIRECTLY_ACTIVATES, DIRECTLY_INHIBITS, TRANSITIVELY_PROVIDES_INPUT_FOR, DIRECTLY_PROVIDES_INPUT_FOR]

RMAP = {
    CAUSALLY_UPSTREAM_OF_OR_WITHIN: {},
    REGULATES_IN_OTHER_ORGANISM: {},

    REGULATES: {'direction':0, 'controls':True},
    NEGATIVELY_REGULATES: {'direction':-1, 'controls':True},
    POSITIVELY_REGULATES: {'direction':+1, 'controls':True},

    #INDIRECTLY_REGULATES: {'interacts':False, 'direction':0, 'controls':True},
    INDIRECTLY_ACTIVATES: {'interacts':False, 'direction':+1, 'controls':True, 'symbol':'..>'},
    INDIRECTLY_INHIBITS: {'interacts':False, 'direction':-1, 'controls':True, 'symbol':'..|'},

    DIRECTLY_REGULATES: {'interacts':True, 'direction':0, 'controls':True, 'symbol':'-o'},
    DIRECTLY_ACTIVATES: {'interacts':True, 'direction':+1, 'controls':True, 'symbol':'->'},
    DIRECTLY_INHIBITS: {'interacts':True, 'direction':-1, 'controls':True, 'symbol':'-|'},

    CAUSALLY_UPSTREAM_OF: {},
    IMMEDIATELY_CAUSALLY_UPSTREAM_OF: {'interacts':True},

    DIRECTLY_PROVIDES_INPUT_FOR: {},
    TRANSITIVELY_PROVIDES_INPUT_FOR: {}
}

def get_relation_properties(p):
    return RMAP[p.uriref]

class Model:
    """
    Represents a collection of connected LEGO units, the backbone of which is a set of activities connected by causal relationships
    """
    def __init__(self, ontmgr=None):    
        """
        A model wraps an OWLOntology. All objects in the model (activities, locations) are individuals in the ontology model,
        and all connections are OWLFacts
        """
        self.ontology = ontmgr
        self.objmap = {}
        self.nodes = []
        self.activators = []
        self.generate()

    @property
    def individuals(self):
        return self.ontology.all_individual()

    @property
    def all_activity(self):
        return self.all_node_by_type(Activity)

    @property
    def all_evidence(self):
        return self.all_node_by_type(Evidence)

    def all_node_by_type(self, cls):
        return [n for n in self.objmap.values() if isinstance(n,cls)]

    def in_range_of(self, pref):
        p = self.ontology.get_property(pref)
        objs = []
        for i in self.individuals:
            for f in i.facts_out(p):
                objs.append(f.o)
            for f in i.facts_out():
                for a in f.annotations:
                    if a.prop == p:
                        objs.append(a.value_as_individual)
        return objs

    def add_typed_object(self, owlobj, cls):
        self.objmap[owlobj.id] = cls(self, owlobj)

    def generate(self):
        for obj in self.in_range_of(LEGO.evidence):
            self.add_typed_object(obj, Evidence)
        for obj in self.in_range_of(OCCURS_IN):
            self.add_typed_object(obj, Location)
        for obj in self.in_range_of(ENABLED_BY):
            self.add_typed_object(obj, Molecular)
        for i in self.individuals:
            if i.id not in self.objmap:
                ## TODO: Fix unsafe assumption
                self.add_typed_object(i, Activity)


class LegoObject:
    def __init__(self, model=None, owlobj=None):    
        self.owlobject = owlobj
        self.model = model

class Node(LegoObject):

    def __str__(self):
        return "{:s} [{:s}]".format(self.id, ",".join(map(str,self.types)))

    
    @property
    def id(self):
        return self.owlobject.id

    @property
    def types(self):
        return self.owlobject.types

    def facts_out(self, p=None):
        return self.owlobject.facts_out(p)

    def facts_in(self, p=None):
        return self.owlobject.facts_in(p)

    def typed_facts_out(self, p, cls):
        return [cls(self.model, f) for f in self.facts_out(p)]
            
class Occurrent(Node):

    @property
    def code(self):
        return 'o'

    @property
    def location_assertions(self):
        return self.typed_facts_out(OCCURS_IN, LocationAssertion)

class MaterialEntity(Node):

    @property
    def code(self):
        return 'me'

class Molecular(MaterialEntity):

    @property
    def code(self):
        return 'mol'


class Activity(Occurrent):

    @property
    def code(self):
        return 'a'

    @property
    def enabled_by_assertions(self):
        return self.typed_facts_out(ENABLED_BY, EnabledByAssertion)

    @property
    def causal_assertions(self):
        l = []
        for p in CAUSAL_RELATIONS:
            l += self.typed_facts_out(p, CausalAssertion)
        return l

class Process(Occurrent):

    @property
    def code(self):
        return 'p'


class Location(Node):

    @property
    def code(self):
        return 'l'

class Evidence(Node):


    @property
    def code(self):
        return 'e'


class Edge(LegoObject):

    @property
    def type(self):
        return self.owlobject.p

    @property
    def relation_properties(self):
        return get_relation_properties(self.type)

    @property
    def about(self):
        return self.owlobject.s

    @property
    def filler(self):
        return self.owlobject.o

    @property
    def all_evidence(self):
        evs = []
        for a in self.owlobject.annotations:
            if a.prop.id == LEGO.evidence:
                evs.append(a.value)

        return evs

class LocationAssertion(Edge):

    @property
    def code(self):
        return 'l'

    @property
    def location(self):
        return self.filler

    @property
    def location_types(self):
        return self.location.types


class EnabledByAssertion(Edge):

    @property
    def code(self):
        return 'e'

    @property
    def molecule(self):
        return self.filler

    @property
    def molecule_types(self):
        return self.molecule.types

class CausalAssertion(Edge):

    @property
    def code(self):
        return 'aa'

    @property
    def affects(self):
        return self.filler

    @property
    def direction(self):
        p = self.relation_properties
        if 'direction' in p:
            return p['direction']
        else:
            return 0

    @property
    def is_controlling(self):
        p = self.relation_properties
        if 'controls' in p:
            return p['controls']
        else:
            return False

    @property
    def affects_types(self):
        return self.affects.types

class EvidenceAssertion(Edge):

    @property
    def code(self):
        return 'l'

    @property
    def evidence(self):
        return self.filler

        
    



