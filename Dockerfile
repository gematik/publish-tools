FROM alpine:3.22@sha256:4b7ce07002c69e8f3d704a9c5d6fd3053be500b7f1c69fc0d80990c2ad8dd412 AS base

# Install python/pip
RUN apk add --update --no-cache python3 py3-pip pipx

FROM base

# Add non-root user to run the application
RUN addgroup -S publisher && adduser -S publisher -G publisher

COPY --chown=publisher:publisher . /opt/publisher

WORKDIR /opt/publisher

## Install the application in a virtualenv
USER publisher

RUN pipx install .

ENTRYPOINT [ "/home/publisher/.local/share/pipx/venvs/publish-tools/bin/publishtools" ]
