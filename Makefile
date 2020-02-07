TMPSPHINXDIR = tmp_sphinx

.PHONY: *

lint:
	tox -e lint

md_docs:
	rm -rf $(TMPSPHINXDIR)
	rm -rf docs/markdown
	sphinx-apidoc -o $(TMPSPHINXDIR) las sphinx-apidoc --full
	make --directory $(TMPSPHINXDIR) markdown
	mv $(TMPSPHINXDIR)/_build/markdown docs

test:
	tox
