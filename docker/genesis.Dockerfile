FROM rust:1.96-bookworm AS build
# rust-toolchain.toml pins a Windows target; override to the container's native toolchain
ENV RUSTUP_TOOLCHAIN=stable
WORKDIR /app
COPY Cargo.toml Cargo.lock rust-toolchain.toml ./
COPY crates ./crates
RUN cargo build --locked --release -p project-ai-genesis-emitter

FROM debian:bookworm-slim AS runtime
RUN useradd --create-home --uid 10001 genesis
COPY --from=build /app/target/release/project-ai-genesis-emitter /usr/local/bin/genesis-emitter
USER 10001:10001
EXPOSE 8080
CMD ["genesis-emitter", "serve", "0.0.0.0:8080"]
