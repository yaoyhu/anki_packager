# Detect operating system
ifeq ($(OS),Windows_NT)
    SHELL := powershell.exe
    .SHELLFLAGS := -NoProfile -Command
    RM = Remove-Item -Force -Recurse
    FOLDER_SET = $$env:FOLDER="$$(Get-Location)"
else
    SHELL := /bin/bash
    RM = rm -rf
    FOLDER_SET = export FOLDER=$$(pwd)
endif

IMAGE_NAME = apkger
CONTAINER_NAME = apkger
VOLUME_NAME = apkger-dicts

.PHONY: build run shell clean help

# Build Docker image and create persistent volume
build:
	docker build -t $(IMAGE_NAME) .
	docker volume create $(VOLUME_NAME)

run:
	docker run --rm \
		--name $(CONTAINER_NAME) \
		-v $(VOLUME_NAME):/app/dicts \
		$(IMAGE_NAME)

# Enter shell in container with volume mounted
shell:
	docker run -it --rm \
		--name $(CONTAINER_NAME) \
		-v $(VOLUME_NAME):/app/dicts \
		-v $(shell pwd)/config:/app/config \
		-v $(shell pwd):/app \
		--entrypoint /bin/bash \
		$(IMAGE_NAME)

clean:
	-docker rmi $(IMAGE_NAME)
	-docker volume rm $(VOLUME_NAME)

help:
	@echo "Available targets:"
	@echo "  build           - Build Docker image and create persistent volume"
	@echo "  run             - Run container with mounted current directory"
	@echo "  shell           - Enter shell in container with volume mounted"
	@echo "  clean           - Remove container and image"
	@echo "  help            - Show this help message"
