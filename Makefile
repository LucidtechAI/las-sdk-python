TMPSPHINXDIR = tmp_sphinx

FILE = /tmp/prism.cid

lint:
	tox -e lint

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
