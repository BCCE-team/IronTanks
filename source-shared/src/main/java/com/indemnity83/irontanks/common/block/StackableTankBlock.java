
package com.indemnity83.irontanks.common.block;

import buildcraft.factory.block.ITankBlockConnector;
import net.minecraft.world.level.block.state.BlockBehaviour;

public class StackableTankBlock extends TankBlock implements ITankBlockConnector {
    public StackableTankBlock(int capacityBuckets, float hardness, float resistance) {
        super(capacityBuckets, hardness, resistance);
    }

    public StackableTankBlock(int capacityBuckets, float hardness, float resistance, BlockBehaviour.Properties properties) {
        super(capacityBuckets, hardness, resistance, properties);
    }
}
