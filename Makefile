
test: test_abox test_gaf test_lego test_networkx test_networkx_abox test_ontology test_properties test_reasoner

test_%: tests/test_%.py 
	nosetests $<
