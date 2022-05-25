
VERSION := 0.0.2
IMAGE := naddeoa/flyte-whylogs-workflow:$(VERSION)
ENTRY := ./flyte/workflows/example.py

.PHONY:dependencies image run console

default: dependencies image console run

dependencies:
	pip install whylogs-1.0.0rc0-py3-none-any.whl flytekit-0.0.0+develop-py2.py3-none-any.whl

image:
	docker build . -t $(IMAGE)
	docker push $(IMAGE)

console:
	flytectl demo start

run:
	pyflyte run --image $(IMAGE) --remote $(ENTRY) wf --n 500 --mean 42 --sigma 20
