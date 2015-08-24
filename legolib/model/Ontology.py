__author__ = 'cjm'

import logging

import rdflib
from rdflib import Namespace
from rdflib import BNode
from rdflib.namespace import RDF
from rdflib.namespace import RDFS
from rdflib.namespace import OWL

class OntologyManager:
    def __init__(self, rdfg=None):
        self.graph = rdfg
        self.prefix_map = {}
        self.reverse_prefix_map = {}
        self.object_map = {
            'o' : {},
            'c' : {},
            'p' : {},
            'i' : {}
        }

    def get_object(self,owltype, objref):
        m = self.object_map[owltype]
        k = str(objref)
        if (k in m):
            return m[k]
        else:
            obj = None
            if owltype == 'c':
                obj = OWLClass(self, objref)
            elif owltype == 'p':
                obj = OWLProperty(self, objref)
            elif owltype == 'i':
                obj = OWLIndividual(self, objref)
            m[k] = obj
            return obj


    def add_object(self,obj):
        obj.set_ontology(self)
        self.object_map[str(obj)] = obj

    def all_cls(self):
        cs = []
        for c in self.graph.subjects(RDF.type, OWL.Class):
            cs.append(self.get_cls(c))
        return cs

    def get_cls(self, ref):
        return self.get_object('c', ref)
    def get_individual(self, ref):
        return self.get_object('i', ref)

    def get_owltypes(self, obj):
        for s in self.graph.objects(obj, RDF.type):
            obj.add_superclass(s)

    def reduce_to_classes(self, refs):
        m2c = lambda uriref : self.get_cls(uriref)
        return map(m2c, filter(is_not_bnode, refs))


class OWLObject:
    def __init__(self, mgr, uriref):    
        self.uriref = uriref
        self.manager = mgr

    def rdfgraph(self):
        return self.manager.graph

    def curie(self, cmap={}):
        return

    def ann(self, p, default=None):
        g = self.rdfgraph()
        uriref = self.uriref
        vs = list(g.objects(uriref, p))
        if (len(vs) == 0):
            return default
        else:
            return str(vs[0].value)

    def label(self, default=None):
        return self.ann(RDFS.label, default)

    def preflabel(self, default=None):
        g = self.rdfgraph()
        uriref = self.uriref
        labeltups = sorted(g.preferredLabel(uriref, lang='en'))
        if (len(labeltups) == 0):
            labels = g.label(uriref)
            if (len(labeltups) == 0):
                return default
            else:
                return labels[0]
        else:
            return labeltups[0][1]
        
    def facts_out():
        return
    def facts_in():
        return


class OWLClass(OWLObject):
    def __str__(self):
        return self.uriref

    def superclasses(self):
        return self.manager.reduce_to_classes(self.rdfgraph().objects(self.uriref, RDFS.subClassOf))

    def superclass_expressions(self):
        return self.manager.map_to_class_expressions(self.rdfgraph().objects(self.uriref, RDFS.subClassOf))

    def svf_superclasses(self, p):
        g = self.rdfgraph()
        vs = []
        for s in g.objects(self.uriref, RDFS.subClassOf):
            if (s, OWL.onProperty, p) in g:
                 vs.append(self.manager.get_cls(g.value(s, OWL.someValuesFrom, None)))
        
        return vs

class OWLIndividual(OWLObject):
    def __str__(self):
        return self.uriref+' "'+str(self.types)+'"'
    

class OWLProperty(OWLObject):
    def __str__(self):
        return self.uriref

def is_bnode(uriref):
    return isinstance(uriref, BNode)

def is_not_bnode(uriref):
    return not(is_bnode(uriref))
        
