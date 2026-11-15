package com.indemnity83.irontanks.client;

import buildcraft.factory.client.render.RenderTank;
import com.indemnity83.irontanks.common.registry.IronTanksBlockEntities;
import net.fabricmc.api.ClientModInitializer;
import net.minecraft.client.renderer.blockentity.BlockEntityRenderer;
import net.minecraft.client.renderer.blockentity.BlockEntityRenderers;
import net.minecraft.world.level.block.entity.BlockEntityType;

/** Client-only Fabric entrypoint; never classloaded by the dedicated server. */
public final class IronTanksClient implements ClientModInitializer {
    @Override
    public void onInitializeClient() {
        registerTankRenderer(IronTanksBlockEntities.TANK.get());
        registerTankRenderer(IronTanksBlockEntities.CREATIVE_TANK.get());
        registerTankRenderer(IronTanksBlockEntities.VOID_TANK.get());
    }

    @SuppressWarnings({"rawtypes", "unchecked"})
    private static void registerTankRenderer(BlockEntityType<?> type) {
        // The BCCE renderer is typed to its base TileTank, while our registered
        // entity types are concrete subclasses with the same render contract.
        BlockEntityRenderers.register((BlockEntityType) type,
            context -> (BlockEntityRenderer) new RenderTank(context));
    }
}
