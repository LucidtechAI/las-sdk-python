TMPSPHINXDIR = tmp_sphinx

.PHONY: *

FILE = /tmp/prism.cid

lint:
	tox -e lint

md_docs:
	rm -rf $(TMPSPHINXDIR)
	rm -rf docs/markdown
	sphinx-apidoc  --full -o $(TMPSPHINXDIR) las sphinx-apidoc las/client.py las/api_client.py las/credentials.py las/prediction.py
	make --directory $(TMPSPHINXDIR) markdown
	mv $(TMPSPHINXDIR)/_build/markdown docs

test: prism-start
	@echo "Running test suite..."
	tox

prism-start: cleanup
	@echo "Starting mock API..."
	docker run \
		--init \
		--detach \
		-p 4010:4010 \
		-h 0.0.0.0 \
		stoplight/prism:3 mock -d \
		https://raw.githubusercontent.com/LucidtechAI/las-docs/master/apis/dev/oas.json
	@echo "Mock API started."

cleanup:
ifeq ($(shell test -e $(FILE)),)
	@echo "Cleaning up..."
	$(shell docker stop $($(shell cat FILE)) 2>/dev/null)
	$(shell rm $(FILE) 2>/dev/null)
else
	@echo "Nothing to clean up."
endif
