
package com.indemnity83.irontanks.common.block;

import buildcraft.factory.block.BlockTank;
import buildcraft.lib.tile.TileBC_Neptune;
import com.indemnity83.irontanks.common.blockentity.TankTile;
import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.block.state.BlockState;
import javax.annotation.Nullable;

import java.util.List;
import java.util.function.Consumer;

public class TankBlock extends BlockTank {
    private static final int MILLIBUCKETS_PER_BUCKET = 1_000;
    private final int capacityBuckets;

    public static BlockBehaviour.Properties createProperties() {
        return defaultProperties();
    }

    public TankBlock(int capacityBuckets, float hardness, float resistance) {
        this(capacityBuckets, hardness, resistance, createProperties());
    }

    protected TankBlock(int capacityBuckets, float hardness, float resistance, BlockBehaviour.Properties properties) {
        super(properties.strength(hardness, resistance).requiresCorrectToolForDrops().noOcclusion());
        this.capacityBuckets = capacityBuckets;
    }

    public final int getCapacityBuckets() {
        return capacityBuckets;
    }

    public final int getCapacityMb() {
        return capacityBuckets * MILLIBUCKETS_PER_BUCKET;
    }

    @Override
    public TileBC_Neptune newBlockEntity(BlockPos pos, BlockState state) {
        return new TankTile(pos, state, getCapacityMb());
    }

    @Override
    public void appendHoverText(ItemStack stack, @Nullable BlockGetter level, List<Component> tooltip, TooltipFlag flag) {
        appendTankTooltip(tooltip::add);
    }

    public final void appendTankTooltip(Consumer<Component> tooltip) {
        tooltip.accept(Component.translatable("irontanks.tooltip.capacity", capacityBuckets).withStyle(ChatFormatting.GRAY));
        appendExtraTooltip(tooltip);
    }

    protected void appendExtraTooltip(Consumer<Component> tooltip) {
    }
}
