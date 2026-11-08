
package com.indemnity83.irontanks.common.block;

import buildcraft.factory.block.ITankBlockConnector;
import net.minecraft.core.Direction;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.properties.BooleanProperty;
import net.minecraft.world.level.block.state.properties.Property;
import net.minecraft.world.level.block.state.BlockBehaviour;

public class StackableTankBlock extends TankBlock implements ITankBlockConnector {
    public StackableTankBlock(int capacityBuckets, float hardness, float resistance) {
        super(capacityBuckets, hardness, resistance);
    }

    public StackableTankBlock(int capacityBuckets, float hardness, float resistance, BlockBehaviour.Properties properties) {
        super(capacityBuckets, hardness, resistance, properties);
    }

    /**
     * The tank model has cullface-tagged end caps. In addition to vanilla shape
     * occlusion, explicitly skip them at BCCE tank-column joints, including
     * mixed BuildCraft / Iron Tanks columns and translucent tank textures.
     *
     * JOINED_BELOW belongs to the upper block (also for BCCE's own tank).
     * Consult that state instead of hiding a cap merely because another tank
     * happens to be adjacent: creative/void tanks are not column connectors.
     */
    @Override
    public boolean skipRendering(BlockState state, BlockState other, Direction side) {
        if (other.getBlock() instanceof ITankBlockConnector) {
            if (side == Direction.DOWN && joinsTankBelow(state)) {
                return true;
            }
            if (side == Direction.UP
                    && joinsTankBelow(other)) {
                return true;
            }
        }
        return super.skipRendering(state, other, side);
    }

    private static boolean joinsTankBelow(BlockState state) {
        // Query the property actually registered by the block. BCCE's
        // BuildCraftProperties is an internal API and must not be imported by addons.
        Property<?> property = state.getBlock().getStateDefinition().getProperty("joined_below");
        return property instanceof BooleanProperty joined
                && state.hasProperty(joined)
                && state.getValue(joined);
    }
}
