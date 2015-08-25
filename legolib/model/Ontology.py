__author__ = 'cjm'

import logging

import yaml
import rdflib
from rdflib import Namespace
from rdflib import BNode
from rdflib import Literal
from rdflib.namespace import RDF
from rdflib.namespace import RDFS
from rdflib.namespace import OWL

OBO = Namespace('http://purl.obolibrary.org/obo/')
OIO = Namespace('http://www.geneontology.org/formats/oboInOwl#')

class OntologyManager:
    """
    An OntologyManager is a facade on top of an rdflib graph. The Objects returned from this API are thin wrappers that delegate calls back to rdflib
    """

    def __init__(self, rdfg=None):
        self.graph = rdfg
        self.prefix_map = {}
        self.reverse_prefix_map = {}

        # Note: punning is supported; the same URI can be
        # in different maps.
        # Only 3 types for now.
        # TBD: conflate all 3 property types?
        self.object_map = {
            'o' : {},
            'c' : {},
            'p' : {},
            'i' : {}
        }

    def load_prefix_map(self, fn):
        f = open(fn, 'r') 
        self.prefix_map = yaml.load(f)

    def sync_with_rdfgraph(self):
        for k in self.object_map:
            self.object_map[k] = {}

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

    def all_individual(self):
        return map(self.get_individual, self.graph.subjects(RDF.type, OWL.NamedIndividual))

    def all_property(self):
        g = self.graph
        ps = []
        # TBD: APs, DPs?
        for p in g.subjects(RDF.type, OWL.ObjectProperty):
            ps.append(self.get_property(p))
        return ps

    def get_cls(self, ref):
        return self.get_object('c', ref)

    def get_property(self, ref):
        return self.get_object('p', ref)

    def get_individual(self, ref):
        return self.get_object('i', ref)

    def get_fact(self, t):
        return OWLFact(self, t)

    def get_owltypes(self, obj):
        for s in self.graph.objects(obj, RDF.type):
            obj.add_superclass(s)

    def reduce_to_classes(self, refs):
        """
        for every non-blank node, translate the URIRef to an OWLClass
        """
        # maybe I should let go of latent lispiness and use list comprehensions...
        m2c = lambda uriref : self.get_cls(uriref)
        return map(m2c, filter(is_not_bnode, refs))

    def reduce_to_facts(self, triples):
        """
        triples to facts. TODO: hash
        """
        m2c = lambda t : self.get_fact(t)
        return map(m2c, filter(is_ope, triples))


class OWLObject:
    """
    Abstract superclass of all OWL Objects.

    Note that the OWLObject contains only a reference to an ontology manager, plus
    a reference to the rdflib.URIRef object. All calls to access information are delegated.
    """
    def __init__(self, mgr, uriref):    
        self.uriref = uriref
        self.manager = mgr

    def __str__(self):
        if self.label:
            return '{:s} "{:s}"'.format(self.id, self.label)
        else:
            return self.id

    def rdfgraph(self):
        return self.manager.graph

    @property
    def id(self):
        """
        Contracts the URI into a short prefixed ID, aka CURIE
        """
        uri = "{:s}".format(str(self.uriref))
        id = uri
        for prefix,uribase in self.manager.prefix_map.items():
            if (uri.startswith(uribase)):
                new_id = uri.replace(uribase,prefix+":")
                if id is None or len(new_id) < len(id):
                    id = new_id
        return id

    def ann(self, p, default=None):
        """
        Single-valued annotation
        """
        g = self.rdfgraph()
        uriref = self.uriref
        vs = list(g.objects(uriref, p))
        if (len(vs) == 0):
            return default
        else:
            return str(vs[0].value)

    def anns(self, p, default=None):
        """
        Multi-valued annotation
        """
        g = self.rdfgraph()
        uriref = self.uriref
        return [v.value for v in g.objects(uriref, p)]

    @property
    def label(self, default=None):
        """
        Returns the label used for the class.

        This assumes maximum one label; will pick
        arbitrary label if multiple available
        """
        return self.ann(RDFS.label, default)

    @property
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

    @property
    def definition(self, default=None):
        """
        Returns the definition used for the class.

        This assumes maximum one definition; will pick
        arbitrary label if multiple available.

        TODO: make the AP configurable
        """
        return self.ann(OBO.IAO_0000115, default)

    # TODO: make this a property?
    def exactSynonyms(self):
        """
        Returns the exact synonyms for the object
        """
        return self.anns(OIO.hasExactSynonym)
        


class OWLClass(OWLObject):

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

    #def __str__(self):
    #    return "{:s} :: {:s}".format(self.id, ",".join(map(str,self.types())))

    def types(self):
        types = [t for t in self.rdfgraph().objects(self.uriref, RDF.type) if t != OWL.NamedIndividual]
        return self.manager.reduce_to_classes(types)

    def type_expressions(self):
        return self.manager.map_to_class_expression(self.rdfgraph().objects(self.uriref, RDF.type))

    def individuals_out(self, p=None):
        return self.manager.map_to_class_expression(self.rdfgraph().objects(self.uriref, p))
    def individuals_in(self, p=None):
        return self.manager.map_to_class_expression(self.rdfgraph().subjects(p, self.uriref))

    def facts_out(self, p=None):
        return self.manager.reduce_to_facts(self.rdfgraph().triples((self.uriref, p, None)))
    def facts_in(self, p=None):
        return self.manager.reduce_to_facts(self.rdfgraph().triples((None, p, self.uriref)))
    

class OWLProperty(OWLObject):

    @property
    def is_transitive(self):
        return OWL.TransitiveProperty in self.rdfgraph().objects(self.uriref, RDF.type);

class OWLFact(OWLObject):
    def __init__(self, mgr, t):
        self.manager = mgr
        self._s = t[0]
        self._p = t[1]
        self._o = t[2]
        self.triple = t
    
    def s(self):
        return self.manager.get_individual(self._s)

    def p(self):
        return self.manager.get_property(self._p)

    def o(self):
        return self.manager.get_individual(self._o)

    def __str__(self):
        return "{:s}-->[{:s}]-->{:s}".format(str(self.s()), str(self.p()), str(self.o()))

def is_bnode(uriref):
    return isinstance(uriref, BNode)

def is_not_bnode(uriref):
    return not(is_bnode(uriref))
        
def is_ope(t):
    return not(is_not_ope(t))

def is_not_ope( t ):
    (s,p,o) = t
    return p == RDF.type or isinstance(o,Literal)

