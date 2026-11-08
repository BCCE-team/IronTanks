
package com.indemnity83.irontanks.common.block;

import buildcraft.factory.block.BlockTank;
import buildcraft.lib.tile.TileBC_Neptune;
import com.indemnity83.irontanks.common.blockentity.TankTile;
import net.minecraft.network.chat.Style;
import net.minecraft.core.BlockPos;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.block.state.BlockState;

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
        // Match BCCE BlockTank: the model's top/bottom cullfaces must see an
        // occluding neighbour so both internal end caps disappear in a tank stack.
        // In particular, do not call noOcclusion() on ordinary tanks here.
        super(properties.strength(hardness, resistance).requiresCorrectToolForDrops());
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

    //? if <1.21.11 {
    /*?
    @Override
    public void appendHoverText(ItemStack stack, Item.TooltipContext context, List<Component> tooltip, TooltipFlag flag) {
        appendTankTooltip(tooltip::add);
    }
    ?*/
    //? }

    public final void appendTankTooltip(Consumer<Component> tooltip) {
        tooltip.accept(Component.translatable("irontanks.tooltip.capacity", capacityBuckets).withStyle(Style.EMPTY.withColor(0xAAAAAA)));
        appendExtraTooltip(tooltip);
    }

    protected void appendExtraTooltip(Consumer<Component> tooltip) {
    }
}
