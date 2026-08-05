FROM alpine/git:2.49.1 AS source
RUN git clone https://github.com/frstrtr/p2pool-merged-v36.git /src && cd /src && git checkout 44a10f30ea4fc8a2b60dfb47d5df7fc3b010ede7
FROM ubuntu:22.04
RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates wget build-essential libssl-dev libffi-dev && rm -rf /var/lib/apt/lists/* && cd /tmp && wget -q https://downloads.python.org/pypy/pypy2.7-v7.3.17-linux64.tar.bz2 && echo '9f3497f87b3372d17e447369e0016a4bec99a6b4d2a59aba774a25bfe4353474  pypy2.7-v7.3.17-linux64.tar.bz2' | sha256sum -c - && tar xjf pypy2.7-v7.3.17-linux64.tar.bz2 -C /opt && ln -s /opt/pypy2.7-v7.3.17-linux64/bin/pypy /usr/local/bin/pypy && wget -q https://bootstrap.pypa.io/pip/2.7/get-pip.py && pypy get-pip.py && pypy -m pip install --no-cache-dir incremental==21.3.0 && pypy -m pip install --no-cache-dir twisted==20.3.0 pycryptodome scrypt==0.8.22 ecdsa==0.19.1 && rm -rf /tmp/*
COPY --from=source /src /app
COPY p2pool-start.sh /usr/local/bin/p2pool-start
# The pinned upstream explicitly defines PERSIST=False with no bootstrap peers
# as its private/solo mode. Keep this image incapable of joining the public
# Litecoin P2Pool sharechain even if runtime flags are accidentally changed.
RUN sed -i 's/^PERSIST = True$/PERSIST = False/' /app/p2pool/networks/litecoin.py \
    && sed -i '/^BOOTSTRAP_ADDRS = \[/,/^\]/c\BOOTSTRAP_ADDRS = []' /app/p2pool/networks/litecoin.py \
    && grep -q '^PERSIST = False$' /app/p2pool/networks/litecoin.py \
    && grep -q '^BOOTSTRAP_ADDRS = \[\]$' /app/p2pool/networks/litecoin.py \
    && useradd -u 1000 -m p2pool \
    && chown -R 1000:1000 /app \
    && chmod 755 /usr/local/bin/p2pool-start
WORKDIR /app
USER 1000:1000
ENTRYPOINT ["p2pool-start"]
