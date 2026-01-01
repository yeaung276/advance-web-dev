from rest_framework import serializers
from . import models


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Event
        fields = ["id", "name"]


class EventOSCSchemaSerializer(serializers.ModelSerializer):
    def to_representation(self, instance: models.Event):
        # Denormalize the detail into original OSC data schema
        sources = []

        host_galaxy = [{"name": g.galaxy.name, "source": g.source} for g in instance.host_galaxies.all()]  # type: ignore

        claimed_type = [{"name": c.sub_type.name, "source": c.source} for c in instance.claimed_types.all()]  # type: ignore

        attributes = instance.attributes.all()  # type: ignore

        return {
            instance.name: {
                "schema": "https://github.com/astrocatalogs/supernovae/blob/d3ef5fc/SCHEMA.md",
                "name": instance.name,
                "sources": sources,
                "hostgalaxy": aliasAndMergeSources(host_galaxy, sources, "name"),
                "claimedtype": aliasAndMergeSources(claimed_type, sources, "name"),
                "lumdist": aliasAndMergeSources(
                    [
                        {
                            "name": "lumdist",
                            "source": attr.source,
                            "value": attr.value,
                            "unit": attr.unit,
                        }
                        for attr in attributes
                        if attr.name == "lumdist"
                    ],
                    sources,
                    "value",
                ),
                "velocity": aliasAndMergeSources(
                    [
                        {
                            "name": "velocity",
                            "source": attr.source,
                            "value": attr.value,
                            "unit": attr.unit,
                        }
                        for attr in attributes
                        if attr.name == "velocity"
                    ],
                    sources,
                    "value",
                ),
                "redshift": aliasAndMergeSources(
                    [
                        {
                            "name": "redshift",
                            "source": attr.source,
                            "value": attr.value,
                            "unit": attr.unit,
                        }
                        for attr in attributes
                        if attr.name == "redshift"
                    ],
                    sources,
                    "value",
                ),
                "maxabsmag": aliasAndMergeSources(
                    [
                        {
                            "name": "maxabsmag",
                            "source": attr.source,
                            "value": attr.value,
                            "unit": attr.unit,
                        }
                        for attr in attributes
                        if attr.name == "maxabsmag"
                    ],
                    sources,
                    "value",
                ),
                "maxappmag": aliasAndMergeSources(
                    [
                        {
                            "name": "maxappmag",
                            "source": attr.source,
                            "value": attr.value,
                            "unit": attr.unit,
                        }
                        for attr in attributes
                        if attr.name == "maxappmag"
                    ],
                    sources,
                    "value",
                ),
            }
        }


def aliasAndMergeSources(entities, sources, dataKey):
    """
    denormalize to OSC schema, If entities has same data value identified by dataKey,
    they will be collapsed into single entity with source represented by comma separated
    source alias: which is the OSC data format.
    """
    # create groups
    grouped = {}
    for e in entities:
        if e[dataKey] in grouped:
            grouped[e[dataKey]].append(e)
            continue
        grouped[e[dataKey]] = [e]

    # merge groups
    result = []
    for group in grouped.values():
        result.append(
            {
                "source": ",".join([get_alias(e["source"], sources) for e in group]),
                **{k: v for k, v in group[0].items() if k != "source"},
            }
        )
    return result


def get_alias(source, sources) -> str:
    """
    Format "sources.Source" to the OSC data schema and add it to the unique source array. Return alias for further use.
    If the source is already in the array, it do nothing and return the alias
    """
    for s in sources:
        if s["id"] == source.id:
            return s["alias"]

    alias = str(
        len(sources) + 2
    )  # 1 for array index connection + 1 for increment counter
    sources.append(
        {
            "id": source.id,
            "name": source.name,
            "url": source.url,
            "doi": source.doi,
            "secondary": source.secondary,
            "alias": alias,
        }
    )
    return alias
