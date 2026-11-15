package com.indemnity83.irontanks.common.blockentity;

import buildcraft.factory.tile.TileTank;
import com.indemnity83.irontanks.common.registry.IronTanksBlockEntities;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.world.level.block.state.BlockState;

/** Isolated void storage: discards only its own fluid and never drains adjacent columns. */
public final class VoidTankTile extends TankTile {
    private static final int TRANSFER_PER_TICK = 80;

    public VoidTankTile(BlockPos pos, BlockState state) {
        this(pos, state, capacityFromState(state));
    }

    public VoidTankTile(BlockPos pos, BlockState state, int capacityMb) {
        super(IronTanksBlockEntities.VOID_TANK.get(), pos, state, capacityMb);
    }

    @Override
    public boolean canConnectTo(TileTank other, Direction direction) {
        return false;
    }

    @Override
    public void update() {
        super.update();
        if (level == null || level.isClientSide()) {
            return;
        }
        int amount = tank.getFluidAmount();
        if (amount > 0) {
            tank.drainInternal(Math.min(amount, TRANSFER_PER_TICK), FluidAction.EXECUTE);
        }
    }
}
