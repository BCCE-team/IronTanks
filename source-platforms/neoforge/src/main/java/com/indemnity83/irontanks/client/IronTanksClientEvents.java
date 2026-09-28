
package com.indemnity83.irontanks.client;

import buildcraft.factory.client.render.RenderTank;
import buildcraft.factory.tile.TileTank;
import com.indemnity83.irontanks.IronTanks;
import com.indemnity83.irontanks.common.registry.IronTanksBlockEntities;
import net.minecraft.client.renderer.blockentity.BlockEntityRenderer;
import net.minecraft.client.renderer.blockentity.BlockEntityRendererProvider;

import net.neoforged.api.distmarker.Dist;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.fml.common.EventBusSubscriber;
import net.neoforged.neoforge.client.event.EntityRenderersEvent;

//? if >=1.21.11 {
@EventBusSubscriber(modid = IronTanks.MODID, value = Dist.CLIENT)
//? } else {
/*?
@EventBusSubscriber(modid = IronTanks.MODID, bus = EventBusSubscriber.Bus.MOD, value = Dist.CLIENT)
?*/
//? }
public final class IronTanksClientEvents {
    private IronTanksClientEvents() {
    }

    @SubscribeEvent
    public static void registerRenderers(EntityRenderersEvent.RegisterRenderers event) {
        event.registerBlockEntityRenderer(IronTanksBlockEntities.TANK.get(), tankRendererProvider());
        event.registerBlockEntityRenderer(IronTanksBlockEntities.CREATIVE_TANK.get(), tankRendererProvider());
        event.registerBlockEntityRenderer(IronTanksBlockEntities.VOID_TANK.get(), tankRendererProvider());
    }

    @SuppressWarnings({"unchecked", "rawtypes"})
    private static BlockEntityRendererProvider tankRendererProvider() {
        return context -> (BlockEntityRenderer) new RenderTank(context);
    }
}
