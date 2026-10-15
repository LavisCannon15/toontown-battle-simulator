# Throw Book scale audit

Measured the actual extracted lawBook model: approximately 94.488 × 121.92 × 28.36 model units. The former scale .5 left its longest side about 33.09 world units on the default level-10 Big Wig (actor scale .542796). The earlier half-size edit was insufficient because it did not measure the asset's native dimensions.

The recipe now uses [.01, .01, .01], producing approximately .513 × .662 × .154 world units on that Cog. The model's original geometry is not normalized by movie_prop, because the caller passes size=None. The recipe scale is applied at the right-hand attachment and multiplied by the Cog actor scale. On release, wrtReparentTo(render) preserves world size; measurement confirmed no scale jump.

Configuration: assets/cog_attack_audit.json, Big Wig|Throw Book, props[0].scale.
Application: cog_choreography.py, prop_movie.attach.

The .01 value is a measured size correction for this simulator, not a verified modern TTR source constant. The regression test now checks actual world extent and unchanged size across hand release, rather than merely checking that geometry exists.
