.PHONY: deploy_prod
deploy_prod:
	python -m twine upload dist/*

.PHONY: deploy_test
deploy_test:
	python -m twine upload --repository testpypi dist/*

.PHONY: build
build: activate_env
	python -m build

.PHONY: activate_env
activate_env:
	. venv/bin/activate