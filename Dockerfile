FROM neo4j:2026.07.1-enterprise

ENV NEO4J_ACCEPT_LICENSE_AGREEMENT=yes
ENV NEO4J_PLUGINS='["apoc"]'
ENV NEO4J_apoc_import_file_enabled=true
ENV NEO4J_apoc_export_file_enabled=true

VOLUME ["/data", "/logs", "/import", "/plugins", "/conf"]

HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=5 \
  CMD wget -qO- http://localhost:7474 || exit 1

CMD ["neo4j"]