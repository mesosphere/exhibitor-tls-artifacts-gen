DOCKER_VERSION := $(shell git describe --tags --abbrev=0)
DOCKER_IMAGE := mesosphere/exhibitor-tls-artifacts-gen:$(DOCKER_VERSION)

.PHONY: docker-image
docker-image:
	docker build -f build/Dockerfile -t $(DOCKER_IMAGE) .

templater:
	curl -L https://raw.githubusercontent.com/johanhaleby/bash-templater/master/templater.sh -o templater
	chmod +x templater

exhibitor-tls-artifacts: docker-image templater
	bash -c "DOCKER_IMAGE=$(DOCKER_IMAGE) ./templater build/exhibitor-tls-artifacts.tpl > exhibitor-tls-artifacts"
	chmod +x exhibitor-tls-artifacts

build: exhibitor-tls-artifacts

.PHONY: docker-image
push-docker: docker-image
	docker push $(DOCKER_IMAGE)
