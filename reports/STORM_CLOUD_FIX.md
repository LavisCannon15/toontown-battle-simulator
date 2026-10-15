# Storm Cloud animation correction

The former implementation started a fixed-size cloud late, compressed its complete channel into 3.5 seconds, drew nine continuous spray beams, and used the generic Squirt reaction.

The dedicated storm_cloud.py builder now follows the local MovieSquirt.__doStormCloud reference: 1.5-second growth, one-second pause, initial trickle, three staggered rain effects, native cloud animation from second 1, and half-second shrink. Hits use a 4.7-second cloud hold; misses use 1.7 seconds. Sounds are scheduled at 2.3 and 4.6 seconds. Impact is 2.9 seconds, with the native Cog soak animation; missed targets dodge at 1.8 seconds. Cloud size/height are adapted to the simulator's character scale.

Rain definitions were inspected and bundled from:
- https://raw.githubusercontent.com/open-toontown/resources/master/phase_5/etc/liquidate.ptf
- https://raw.githubusercontent.com/open-toontown/resources/master/phase_5/etc/trickleLiquidate.ptf

Both use the raindrop sprite from the project's extracted TTR suit-particles model. No external runtime resource dependency was added. The simulator uses one cloud per target rather than the classic reference's duplicated LOD props.

Verification: 91 unit tests passed; dedicated tests verified growth, initial pose, rain systems, different hit/miss durations, native soak, complete live rounds, displayed HP parity, and cleanup. A rendered rain frame was inspected. This checks the available classic choreography with current TTR assets, not parity with unavailable modern TTR sequencing code.
