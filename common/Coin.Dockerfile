FROM alpine:3.22.1@sha256:4bcff63911fcb4448bd4fdacec207030997caf25e9bea4045fa6c8c44de311d1 AS fetch
ARG COIN ARG_VERSION ARG_ARCH TARGETARCH SHA_AMD64 SHA_ARM64
RUN apk add --no-cache ca-certificates curl tar && case "$TARGETARCH" in amd64) archive_arch=x86_64; sha="$SHA_AMD64";; arm64) archive_arch=aarch64; sha="$SHA_ARM64";; *) echo "unsupported architecture: $TARGETARCH" >&2; exit 1;; esac && \
    url="https://github.com/${COIN}-project/${COIN}/releases/download/v${ARG_VERSION}/${COIN}-${ARG_VERSION}-${archive_arch}-linux-gnu.tar.gz" && \
    [ "$COIN" != dogecoin ] || url="https://github.com/dogecoin/dogecoin/releases/download/v${ARG_VERSION}/dogecoin-${ARG_VERSION}-${archive_arch}-linux-gnu.tar.gz" && \
    curl -fL "$url" -o /tmp/coin.tgz && echo "$sha  /tmp/coin.tgz" | sha256sum -c - && mkdir /out && tar -xzf /tmp/coin.tgz --strip-components=2 -C /out "${COIN}-${ARG_VERSION}/bin"
FROM debian:bookworm-slim@sha256:df52e55e3361a81ac1bead266f3373ee55d29aa50cf0975d440c2be3483d8ed3
ARG COIN
COPY --from=fetch /out/ /usr/local/bin/
COPY coin-entrypoint.sh /usr/local/bin/coin-entrypoint
RUN useradd -u 1000 -m coin && chmod 755 /usr/local/bin/coin-entrypoint
USER 1000:1000
STOPSIGNAL SIGTERM
ENTRYPOINT ["coin-entrypoint"]
