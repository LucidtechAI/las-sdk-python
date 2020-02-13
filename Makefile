TMPSPHINXDIR = tmp_sphinx
CID := $(shell cat /tmp/prism.cid)

.PHONY: lint
lint:
	tox -e lint

md_docs:
	rm -rf $(TMPSPHINXDIR)
	rm -rf docs/markdown
	sphinx-apidoc  --full -o $(TMPSPHINXDIR) las sphinx-apidoc las/client.py las/api_client.py las/credentials.py las/prediction.py
	make --directory $(TMPSPHINXDIR) markdown
	mv $(TMPSPHINXDIR)/_build/markdown docs

.PHONY: test
test:
	@echo "Running test suite..."
	tox -e py

.PHONY: prism-start
prism-start:
	@echo "Starting mock API..."
	docker run \
		--init \
		--detach \
		-p 4010:4010 \
		-h 0.0.0.0 \
		stoplight/prism:3.2.8 mock -d -h 0.0.0.0 \
		https://raw.githubusercontent.com/LucidtechAI/las-docs/rest-api-docs/apis/dev/oas.json > /tmp/prism.cid

.PHONY: prism-stop
prism-stop:
ifeq ("$(wildcard /tmp/prism.cid)","")
	@echo "Nothing to stop."
else
	docker stop $(CID)
endif
