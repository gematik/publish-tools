FROM alpine:3.22@sha256:4b7ce07002c69e8f3d704a9c5d6fd3053be500b7f1c69fc0d80990c2ad8dd412 AS base

# Install python/pip
RUN apk add --update --no-cache python3 py3-pip py3-virtualenv

FROM base

# Add non-root user to run the application
RUN addgroup -S publisher && adduser -S publisher -G publisher

COPY --chown=publisher:publisher . /opt/publisher

WORKDIR /opt/publisher

## Create Executable Script that activates the virtualenv and runs the tool
USER root

RUN echo '#!/usr/bin/env sh' > /usr/local/bin/publish-tools && \
    echo '. /home/publisher/.python/venv/bin/activate' >> /usr/local/bin/publish-tools && \
    echo 'python -m publish_tools "$@"' >> /usr/local/bin/publish-tools && \
    chmod +x /usr/local/bin/publish-tools

## Install the application in a virtualenv
USER publisher

RUN python3 -m venv /home/publisher/.python/venv && \
    . /home/publisher/.python/venv/bin/activate && \
    pip install .

ENTRYPOINT [ "/usr/local/bin/publish-tools" ]