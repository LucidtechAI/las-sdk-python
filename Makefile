TMPSPHINXDIR = tmp_sphinx

.PHONY: *

lint:
	tox -e lint

docs:
	rm -rf $(TMPSPHINXDIR)
	sphinx-apidoc -o $(TMPSPHINXDIR) . sphinx-apidoc --full
	make --directory $(TMPSPHINXDIR) markdown
	mv $(TMPSPHINXDIR)/_build/markdown docs

test:
	tox
