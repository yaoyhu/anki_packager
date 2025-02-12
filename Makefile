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

IMAGE_NAME = apkg
CONTAINER_NAME = apkg

.PHONY: build run shell clean check_image

# Build Docker image
build:
	docker build -t $(IMAGE_NAME) .

# Run container with mounted config
run:
	$(FOLDER_SET) && \
	docker run --rm \
		--name $(CONTAINER_NAME) \
		--mount type=bind,source=$$FOLDER,target=/app \
		$(IMAGE_NAME)

# Enter shell in container
shell:
	docker run -it --rm\
		--name $(CONTAINER_NAME) \
		--entrypoint /bin/bash \
		$(IMAGE_NAME)

# Clean up
clean:
	-docker stop $(CONTAINER_NAME)
	-docker rm $(CONTAINER_NAME)
	-docker rmi $(IMAGE_NAME)