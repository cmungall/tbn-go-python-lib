"""

This modules provides objects for working with OWL Ontologies.

The module is a facade over an RDF graph, provided by rdflib. The
Objects in this module are simple delegators that hold a reference to
either a URIRef (in the case of classes, properties and individuals)
or a triple (in the case of axioms).

"""

__author__ = 'cjm'

import logging

import yaml
import rdflib
from legolib.reasoner.BasicReasoner import BasicReasoner
from rdflib import Namespace
from rdflib import BNode
from rdflib import Literal
from rdflib import URIRef
from rdflib.namespace import RDF
from rdflib.namespace import RDFS
from rdflib.namespace import OWL

OBO = Namespace('http://purl.obolibrary.org/obo/')
OIO = Namespace('http://www.geneontology.org/formats/oboInOwl#')

## utility methods
def annotations_to_dict(anns):
    dict = {}
    for ann in anns:
        pid = ann.prop.id
        if not pid in dict:
            dict[pid] = []
        dict[pid].append(ann.str_value)
    return dict

def as_uriref(obj):
    if isinstance(obj,URIRef):
        return obj
    elif isinstance(obj, OWLObject):
        return obj.uriref
    else:
        return None
    

class OntologyManager:
    """
    An OntologyManager is a facade on top of an rdflib graph. The Objects returned from this API are thin wrappers that delegate calls back to rdflib.

    TODO: split this into manager + ontology?
    """

    def __init__(self, rdfg=None):
        self.graph = rdfg
        self.prefix_map = {}
        self.reverse_prefix_map = {}
        self._reasoner = None

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

        # modeled after SciGraph categories map
        self.categories_map = {
            OWL.Class : 'class',
            OWL.NamedIndividual : 'individual'
        }

        # TODO: do not use OIO as default
        self.synonym_properties = [ OIO.hasExactSynonym, OIO.hasRelatedSynonym, OIO.hasBroadSynonym, OIO.hasNarrowSynonym  ]

        self.definition_property = OBO.IAO_0000115

    def load_prefix_map(self, fn):
        """
        Loads curie prefixes from a YAML file
        """
        f = open(fn, 'r') 
        self.prefix_map = yaml.load(f)

    def sync_with_rdfgraph(self):
        for k in self.object_map:
            self.object_map[k] = {}

    def expand_curie(self, k):
        toks = k.split(":")
        if (len(toks) == 2):
            pfx = toks[0]
            if pfx in self.prefix_map:
                return self.prefix_map[pfx] + toks[1]
            else:
                return k
        else:
            return k

    def get_uriref(self, k):
        if isinstance(k, str):
            uri = self.expand_curie(k)
            return URIRef(uri)
        else:
            return k

    def get_object(self,owltype, k):
        objref = self.get_uriref(k)
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

    def all_cls(self):
        cs = []
        for c in self.graph.subjects(RDF.type, OWL.Class):
            cs.append(self.get_cls(c))
        return cs

    def all_individual(self):
        return [self.get_individual(i) for i in self.graph.subjects(RDF.type, OWL.NamedIndividual)]

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

    def get_annotation(self, p, v):
        return OWLAnnotation(self, p, v)

    def get_fact(self, t):
        return OWLFact(self, t)

    def reduce_to_classes(self, urirefs):
        """
        for every non-blank node, translate the URIRef to an OWLClass
        """
        return [self.get_cls(uriref) for uriref in urirefs if not is_bnode(uriref)]

    def reduce_to_facts(self, triples):
        """
        triples to facts. TODO: hash
        """
        return [self.get_fact(t) for t in triples if is_ope(t)]

    @property
    def reasoner(self):
        if not self._reasoner:
            self._reasoner = BasicReasoner(self)
        return self._reasoner

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
    def label(self):
        """
        Returns the label used for the class.

        This assumes maximum one label; will pick
        arbitrary label if multiple available
        """
        return self.ann(RDFS.label)

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
        return self.ann(self.manager.definition_property, default)

    @property
    def synonyms(self):
        """
        Returns the exact synonyms for the object
        """
        syns = []
        for p in self.manager.synonym_properties:
            syns += self.anns(p)
        return syns
        
class OWLClass(OWLObject):


    def superclasses(self):
        """
        Returns asserted named superclasses
        """
        return self.manager.reduce_to_classes(self.rdfgraph().objects(self.uriref, RDFS.subClassOf))

    def subclasses(self):
        """
        Returns asserted named subclasses
        """
        return self.manager.reduce_to_classes(self.rdfgraph().subjects(RDFS.subClassOf, self.uriref))

    def individuals(self):
        """
        Returns asserted instances
        """
        return [self.manager.get_individual(x) for x in self.rdfgraph().subjects(RDF.type, self.uriref)]

    def inferred_individuals(self):
        """
        Returns inferred individuals. TODO: use more efficient method
        """
        inds = []
        for x in self.manager.all_individual():
            if self in x.inferred_types():
                inds.append(x) 
        return inds

    def superclass_expressions(self):
        return self.manager.map_to_class_expressions(self.rdfgraph().objects(self.uriref, RDFS.subClassOf))

    def svf_superclasses(self, p):
        """
        Given C P returns D, where C SubClassOf P some D
        """
        g = self.rdfgraph()
        vs = []
        for s in g.objects(self.uriref, RDFS.subClassOf):
            if (s, OWL.onProperty, p) in g and (s, OWL.someValuesFrom, None) in g:
                 vs.append(self.manager.get_cls(g.value(s, OWL.someValuesFrom, None)))
        return vs

    def svf_superclass_map(self):
        """
        Given C returns a map P=>D*, where C SubClassOf P some D
        """
        g = self.rdfgraph()
        pmap = {}
        for s in g.objects(self.uriref, RDFS.subClassOf):
            if (s, OWL.onProperty, None) in g and (s, OWL.someValuesFrom, None) in g:
                p = self.manager.get_property(g.value(s, OWL.onProperty, None))
                filler = self.manager.get_cls(g.value(s, OWL.someValuesFrom, None))
                if not(p.id in pmap):
                    pmap[p.id] = []
                pmap[p.id].append(filler)
        return pmap

    def inferred_superclasses(self):
        """
        transitive closure of superclasses
        """
        return self.manager.reasoner.inferred_superclasses(self)

    def inferred_subclasses(self):
        """
        transitive closure of subclasses
        """
        return self.manager.reasoner.inferred_subclasses(self)

class OWLIndividual(OWLObject):
    """
    Currently this represents any OWL Individual. May be split into distinct classes for named and anonymous
    """

    @property
    def types(self):
        types = [t for t in self.rdfgraph().objects(self.uriref, RDF.type) if t != OWL.NamedIndividual]
        return self.manager.reduce_to_classes(types)

    @property
    def inferred_types(self):
        return self.manager.reasoner.inferred_superclasses(self.types)

    @property
    def type_expressions(self):
        return self.manager.map_to_class_expression(self.rdfgraph().objects(self.uriref, RDF.type))

    def individuals_out(self, p=None):
        return self.manager.map_to_class_expression(self.rdfgraph().objects(self.uriref, p))
    def individuals_in(self, p=None):
        return self.manager.map_to_class_expression(self.rdfgraph().subjects(p, self.uriref))

    def facts_out(self, p=None):
        return self.manager.reduce_to_facts(self.rdfgraph().triples((self.uriref, as_uriref(p), None)))
    def facts_in(self, p=None):
        return self.manager.reduce_to_facts(self.rdfgraph().triples((None, as_uriref(p), self.uriref)))
    

class OWLProperty(OWLObject):

    """
    Currently this represents any OWL ObjectProperty. May be split into distinct classes for different property types
    """

    # TODO: other characteristics

    @property
    def is_transitive(self):
        return OWL.TransitiveProperty in self.rdfgraph().objects(self.uriref, RDF.type);

    @property
    def is_top(self):
        return self.uriref == OWL.topObjectProperty

    def superproperties(self):
        """
        Returns asserted superproperties
        """
        return [self.manager.get_property(p) for p in self.rdfgraph().objects(self.uriref, RDFS.subPropertyOf)]

class OWLAxiom(OWLObject):
    """
    Any OWL Axiom
    """
    def __init__(self, mgr):
        self.manager = mgr
        self._annotations = []

    @property
    def annotations(self):
        return self._annotations

class OWLAnnotation(OWLObject):
    """
    property-value pair
    """
    def __init__(self, mgr, p, v):
        self.manager = mgr
        self.prop = mgr.get_property(p)
        self.value = v

    def __str__(self):
        return '{:s} "{:s}"'.format(str(self.prop), str(self.value))

    @property
    def as_tuple(self):
        return (self.prop, self.value)

    @property
    def value_as_individual(self):
        if isinstance(self.value, URIRef):
            return self.manager.get_individual(self.value)

    @property
    def value_as_id(self):
        if isinstance(self.value, URIRef):
            # TODO
            tmpobj = OWLObject(self.manager, self.value)
            return tmpobj.id

    @property
    def str_value(self):
        if isinstance(self.value, Literal):
            return self.value.value
        else:
            return self.value_as_id

class OWLFact(OWLAxiom):
    """
    Aka OWL ObjectPropertyAssertion
    """
    def __init__(self, mgr, t):
        self.manager = mgr
        self._s = t[0]
        self._p = t[1]
        self._o = t[2]
        self.triple = t
    
    @property
    def s(self):
        return self.manager.get_individual(self._s)

    @property
    def p(self):
        return self.manager.get_property(self._p)

    @property
    def o(self):
        return self.manager.get_individual(self._o)

    @property
    def axiomrefs(self):
        g = self.rdfgraph()
        siri = self.s.uriref
        piri = self.p.uriref
        oiri = self.o.uriref
        axrefs = []
        for axref in g.subjects(OWL.annotatedSource, siri):
            if (axref,OWL.annotatedTarget,oiri) in g:
                if (axref,OWL.annotatedProperty,piri) in g:
                    axrefs.append(axref)
        return axrefs

    @property
    def annotations(self):
        anns = []
        m = self.manager
        g = m.graph
        for axref in self.axiomrefs:
            for (s,p,o) in g.triples((axref,None,None)):
                if p not in [OWL.annotatedSource, OWL.annotatedTarget, OWL.annotatedProperty, RDF.type]:
                  anns.append(m.get_annotation(p,o))
        return anns

    def __str__(self):
        return "{:s}-->[{:s}]-->{:s}".format(str(self.s), str(self.p), str(self.o))

def is_bnode(uriref):
    """
    True if uriref is a blank node
    """
    return isinstance(uriref, BNode)

# deprecated
def is_not_bnode(uriref):
    return not(is_bnode(uriref))
        
def is_ope(t):
    return not(is_not_ope(t))

def is_not_ope( t ):
    (s,p,o) = t
    return p == RDF.type or isinstance(o,Literal)

