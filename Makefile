
test: ontology_test abox_test reasoner_test 

%_test: tests/test_%.py 
	nosetests $<
