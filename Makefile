TMPSPHINXDIR = tmp_sphinx

.PHONY: *

lint:
	tox -e lint

md_docs:
	rm -rf $(TMPSPHINXDIR)
	rm -rf docs/markdown
	sphinx-apidoc  --full -o $(TMPSPHINXDIR) las sphinx-apidoc las/client.py las/api_client.py las/credentials.py las/prediction.py
	make --directory $(TMPSPHINXDIR) markdown
	mv $(TMPSPHINXDIR)/_build/markdown docs

test:
	tox
