
test: ontology_test

%_test: tests/test_%.py 
	nosetests $<
