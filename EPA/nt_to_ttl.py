from rdflib import Graph
import sys

# Very simple script to transform NT into TTL
# Usage: python nt_to_ttl.py source.nt target.ttl
source = sys.argv[1]
target = sys.argv[2]
graph = Graph()
graph.parse(source, format='nt')
graph.serialize(target, format="ttl")
