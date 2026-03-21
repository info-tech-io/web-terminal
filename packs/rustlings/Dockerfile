# Pack: rustlings — Rust learning exercises
# Child #5 (Phase 1-C), Issue #5
# Base: rust:slim — уже содержит Rust toolchain, не нужен rustup/build-essential
FROM rust:slim

RUN apt-get update && apt-get install -y git && \
    rm -rf /var/lib/apt/lists/*

RUN rustup component add clippy && \
    cargo install rustlings && \
    rm -rf /usr/local/cargo/registry /usr/local/cargo/git

WORKDIR /workspace
COPY scripts/ /scripts/
RUN chmod +x /scripts/*.sh

CMD ["/bin/bash"]
