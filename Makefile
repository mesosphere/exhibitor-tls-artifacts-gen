TAG := $(shell git describe --tags --abbrev=0)
ifeq ($(TAG),)
TAG := $(shell git rev-parse HEAD)
endif

USER := mesosphere
REPO := exhibitor-tls-artifacts-gen
DOCKER_IMAGE := $(USER)/$(REPO):$(TAG)
BIN := exhibitor-tls-artifacts


.PHONY: docker-image
docker-image:
	docker build -f build/Dockerfile -t $(DOCKER_IMAGE) .

templater:
	curl -L https://raw.githubusercontent.com/johanhaleby/bash-templater/8441dfda092b21d45925ff3d0b76f80e4098c19c/templater.sh -o templater
	chmod +x templater

$(BIN): templater
	bash -c "DOCKER_IMAGE=$(DOCKER_IMAGE) ./templater build/exhibitor-tls-artifacts.tpl > exhibitor-tls-artifacts"
	chmod +x exhibitor-tls-artifacts

build: docker-image exhibitor-tls-artifacts

test:
	pytest -vvv -s tests/

.PHONY: docker-image
docker-push: docker-image
	docker push $(DOCKER_IMAGE)

.PHONY: docker-test
docker-test: docker-image
	docker run --entrypoint /bin/sh -t --rm $(DOCKER_IMAGE) -c 'make test'

github-release:
	curl -L https://github.com/aktau/github-release/releases/download/v0.7.2/linux-amd64-github-release.tar.bz2 -o github-release.tar.bz2
	# Our jenkins doesn't support .tar.bz2 archivves
	bunzip2 -c < github-release.tar.bz2 | gzip -c > github-release.tar.gz
	tar xzf github-release.tar.gz
	mv bin/linux/amd64/github-release .
	rm -rf bin github-release.tar.bz2

release: github-release build
	./github-release release -u $(USER) -r $(REPO) \
		-t $(TAG) -n $(TAG)
	./github-release upload -u $(USER) -r $(REPO) -t $(TAG) -n $(BIN) -f $(BIN)
