package com.indemnity83.irontanks.common.registry;

import buildcraft.lib.compat.BlockEntityTypeCompat;
import buildcraft.lib.platform.registry.BCDeferredRegister;
import buildcraft.lib.platform.registry.BCRegistryEntry;
import buildcraft.lib.platform.registry.RegistryBinding;
import com.indemnity83.irontanks.IronTanks;
import com.indemnity83.irontanks.common.blockentity.CreativeTankTile;
import com.indemnity83.irontanks.common.blockentity.TankTile;
import com.indemnity83.irontanks.common.blockentity.VoidTankTile;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.entity.BlockEntityType;

import java.util.function.Supplier;

public final class IronTanksBlockEntities {
    private static final BCDeferredRegister<BlockEntityType<?>> BLOCK_ENTITIES =
        BCDeferredRegister.create("minecraft:block_entity_type", IronTanks.MODID);

    public static final BCRegistryEntry<BlockEntityType<TankTile>> TANK = BLOCK_ENTITIES.register("tank", () ->
        BlockEntityTypeCompat.create(TankTile::new, normalTankBlocks()));
    public static final BCRegistryEntry<BlockEntityType<CreativeTankTile>> CREATIVE_TANK = BLOCK_ENTITIES.register("creative_tank", () ->
        BlockEntityTypeCompat.create(CreativeTankTile::new, IronTanksBlocks.CREATIVE_TANK.get()));
    public static final BCRegistryEntry<BlockEntityType<VoidTankTile>> VOID_TANK = BLOCK_ENTITIES.register("void_tank", () ->
        BlockEntityTypeCompat.create(VoidTankTile::new, IronTanksBlocks.VOID_TANK.get()));

    private IronTanksBlockEntities() {}

    private static Block[] normalTankBlocks() {
        return IronTanksBlocks.NORMAL_TANKS.stream().map(Supplier::get).toArray(Block[]::new);
    }

    public static void register() {
        BLOCK_ENTITIES.register(RegistryBinding.direct());
    }
}
