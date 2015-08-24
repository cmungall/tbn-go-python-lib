__author__ = 'cjm'

import logging

class Model:
    def __init__(self, obj={}):    
        self.id = obj['id']
        self.title = obj['title']
        self.individuals = []
        self.edges = []
    def __str__(self):
        return self.id+' "'+str(self.title)+'"'

    def get_individuals():
        return self.individuals

class Individual:
    def __init__(self, obj={}):    
        self.id = obj['id']
        self.types = obj['types']
    def __str__(self):
        return self.id+' "'+str(self.types)+'"'
    
    def get_facts_out():
        return
    def get_facts_in():
        return

class Activity(Individual):
    def __init__(self, obj={}):
        Individual.__init__(self, obj)

class Fact:
    def __init__(self, obj={}):    
        self.id = obj['id']
        self.types = obj['types']
    def __str__(self):
        return self.id+' "'+str(self.types)+'"'


