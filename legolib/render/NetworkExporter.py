import networkx as nx
from networkx import write_yaml

from legolib.export.Exporter import Exporter

class NetworkExporter(Exporter):
    """
    for networkx
    """

    def __init__(self, ontology_manager):
        self._ontology_manager = ontology_manager
        self._graph = None

    def convert(self):
        o = self._ontology_manager
        g = nx.DiGraph()
        self._graph = g
        for c in o.all_cls():
            self.add_node(c)
            for s in c.superclasses():
                self.add_edge(c,s,'subClassOf')
            for (p,ds) in c.svf_superclass_map().items():
                for d in ds:
                    self.add_edge(c,d,p)
        for i in o.all_individual():
            self.add_node(i)
            for f in i.facts_out():
                self.add_edge(f.s, f.o, f.p)
            
    def add_node(self, n):
        if n.label:
            self._graph.add_node(n.id, label=n.label)
        else:
            self._graph.add_node(n.id)

    def add_edge(self, s,o,p):
        pid = p if isinstance(p,str) else p.id
        self._graph.add_edge(s.id,o.id,type=pid)
        #self._graph.add_edge(s.id,o.id,type=p.id)

    def export_yaml(self,fn=None):
        if not self._graph:
            self.convert()
        write_yaml(self._graph, fn)
        
        
    
