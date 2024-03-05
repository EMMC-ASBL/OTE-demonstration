from pathlib import Path

from tripper import Triplestore

import dlite
from dlite.rdf2 import to_rdf


thisdir = Path(__file__).resolve().parent
for filename in thisdir.glob("*.json"):
    inst = dlite.Instance.from_location("json", filename)

    triples = to_rdf(
        inst,
        standard="emmo",
        base_uri="http://onto-ns.com/data#",
        include_meta=False,
    )

    ts = Triplestore(backend="rdflib")
    ts.bind("emmo", "http://emmo.info/emmo#")
    ts.bind("oteio", "http://emmo.info/oteio.pipeline#")
    ts.add_triples(triples)
    ts.serialize(destination=filename.with_suffix(".ttl"), format="turtle")
