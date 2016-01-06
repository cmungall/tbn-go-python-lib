__author__ = 'cjm'

import logging
import csv
import re
import networkx as nx

class AssociationParser:

    def __init__(self): 
        self.entity_graph = nx.DiGraph()
        self.association_graph = nx.DiGraph()
        self.negative_association_graph =  nx.DiGraph()

    def get_node(self, id, props={}):
        return id
    def make_node(self, id, dict):
        self.entity_graph.add_node(id, dict)
        return id

    @property
    def merged_graph(self):
        return nx.compose(self.association_graph,self.entity_graph)

class GAFParser(AssociationParser):

    def parse(self, f):
        with open(f, 'r', encoding="utf8") as csvfile:
            filereader = csv.reader(csvfile, delimiter='\t', quotechar='\"')
            for row in filereader:
                if re.match('^\!', row[0]):
                    continue
                (db, acc, sym, qualstr, class_id, publiststr, eco, withfrom, aspect, gpname, gpsyn, gptype, gptaxon, assocdate, assigned_by, anext, prodform) = row
                quals = qualstr.split('|') if len(qualstr) > 0 else []
                pubs = publiststr.split('|') if len(publiststr) > 0 else []
                cnode = self.get_node(class_id)
                gpid = db + ':' + acc
                gnode = self.make_node(gpid, {'label':sym, 'taxon':gptaxon, 'type':gptype})
                n = self.association_graph
                if 'NOT' in quals:
                    n = self.negative_association_graph
                n.add_edge(gpid, class_id, aspect=aspect, assigned_by=assigned_by, quals=quals, prodform=prodform, anext=anext, assocdate=assocdate)
        return

                
        


        

        
