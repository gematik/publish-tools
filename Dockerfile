FROM alpine:3.22@sha256:4b7ce07002c69e8f3d704a9c5d6fd3053be500b7f1c69fc0d80990c2ad8dd412 AS base

FROM base AS builder

# Install python/pip
RUN apk add --update --no-cache python3 py3-pip py3-virtualenv && \
    python3 -m venv /opt/python-venv

ENV PATH="/opt/python-venv/bin:${PATH}"

COPY --chown=publisher:publisher . /opt/publisher

WORKDIR /opt/publisher

RUN pip3 install .

FROM base

# Add non-root user to run the application
RUN apk add --update --no-cache python3 && \
    addgroup -S publisher && adduser -S publisher -G publisher

COPY --from=builder /opt/python-venv /opt/python-venv

ENV PATH="/opt/python-venv/bin:${PATH}"

## Install the application in a virtualenv
USER publisher

ENTRYPOINT [ "python", "-m", "publish_tools" ]
