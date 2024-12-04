.PHONY: venv
venv:
	python3 -m venv venv && source venv/bin/activate

.PHONY: install
install: venv
	venv/bin/pip install -r requirements.txt

.PHONY: django
django:
	python step/manage.py runserver

.PHONY: test
test:
	pytest step/contests/tests

.PHONY: run_tests
run_tests: install django test


