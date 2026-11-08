
package com.indemnity83.irontanks.common.blockentity;

import buildcraft.factory.tile.TileTank;

import com.indemnity83.irontanks.common.registry.IronTanksBlockEntities;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.world.level.block.state.BlockState;


public final class VoidTankTile extends TankTile {
    /** Matches the default BuildCraft CE void fluid pipe rate: base fluid rate 10 * 8. */
    private static final int TRANSFER_PER_TICK = 80;

    public VoidTankTile(BlockPos pos, BlockState state) {
        this(pos, state, capacityFromState(state));
    }

    public VoidTankTile(BlockPos pos, BlockState state, int capacityMb) {
        super(IronTanksBlockEntities.VOID_TANK.get(), pos, state, capacityMb);
    }

    // Original Iron Tanks void tanks do not share storage with normal tanks.
    // A joined void column would silently delete fluid from neighbouring tiers.
    @Override
    public boolean canConnectTo(TileTank other, Direction direction) {
        return false;
    }

    @Override
    public void update() {
        super.update();
        //? if >=1.21.11 {
        if (level == null || level.isClientSide()) {
        //? } else {
        /*?
        if (level == null || level.isClientSide) {
        ?*/
        //? }
            return;
        }

        int amount = tank.getFluidAmount();
        if (amount > 0) {
            tank.drainInternal(Math.min(amount, TRANSFER_PER_TICK), FluidAction.EXECUTE);
        }
    }
}
