docker run -it --rm \
  --publish=7474:7474 --publish=7687:7687 \
  --env NEO4J_AUTH=none \
  --env NEO4J_PLUGINS='["apoc","graph-data-science"]' \
  --env NEO4J_dbms_security_procedures_unrestricted=gds.*,apoc.*\
  --env NEO4J_dbms_security_procedures_allowlist=gds.*,apoc.*\
  -v plugins:/plugins\
  -v data:/data\
  neo4j:5.11.0