# Pack: rustlings — Rust learning exercises
# Full implementation: Child #5 (Phase 1-C), Issue #5
FROM ubuntu:22.04

RUN apt-get update && apt-get install -y curl git && \
    rm -rf /var/lib/apt/lists/*

RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
ENV PATH="/root/.cargo/bin:$PATH"

RUN cargo install rustlings

WORKDIR /workspace
COPY scripts/ /scripts/
RUN chmod +x /scripts/*.sh

CMD ["/bin/bash"]
