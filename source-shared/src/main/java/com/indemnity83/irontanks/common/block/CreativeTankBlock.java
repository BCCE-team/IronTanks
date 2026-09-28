
package com.indemnity83.irontanks.common.block;

import buildcraft.lib.tile.TileBC_Neptune;
import com.indemnity83.irontanks.common.blockentity.CreativeTankTile;
import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.network.chat.Component;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.block.state.BlockState;

import java.util.function.Consumer;

public final class CreativeTankBlock extends TankBlock {
    public CreativeTankBlock(int capacityBuckets) {
        super(capacityBuckets, -1.0F, 3_600_000.0F);
    }

    public CreativeTankBlock(int capacityBuckets, BlockBehaviour.Properties properties) {
        super(capacityBuckets, -1.0F, 3_600_000.0F, properties);
    }

    @Override
    public TileBC_Neptune newBlockEntity(BlockPos pos, BlockState state) {
        return new CreativeTankTile(pos, state, getCapacityMb());
    }

    @Override
    protected void appendExtraTooltip(Consumer<Component> tooltip) {
        tooltip.accept(Component.translatable("irontanks.tooltip.creative_tank").withStyle(ChatFormatting.LIGHT_PURPLE));
    }
}
