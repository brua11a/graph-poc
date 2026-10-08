#!/usr/bin/bash
set -e

cypher-shell -a bolt://neo4j:7687 -u "${NEO4J_USER:-neo4j}" -p "${NEO4J_PASSWORD:-neo4j}" -f /queries/schema.cypher
cypher-shell -a bolt://neo4j:7687 -u "${NEO4J_USER:-neo4j}" -p "${NEO4J_PASSWORD:-neo4j}" -f /queries/nodes.cypher
cypher-shell -a bolt://neo4j:7687 -u "${NEO4J_USER:-neo4j}" -p "${NEO4J_PASSWORD:-neo4j}" -f /queries/edges.cypher