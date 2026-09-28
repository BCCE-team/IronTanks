package com.indemnity83.irontanks;

import buildcraft.core.BCCore;
//? if >=1.21.11 {
import buildcraft.lib.compat.transfer.TransferInterop;
//? }
import com.indemnity83.irontanks.common.guide.IronTanksGuide;
import com.indemnity83.irontanks.common.registry.IronTanksBlockEntities;
import com.indemnity83.irontanks.common.registry.IronTanksBlocks;
import com.indemnity83.irontanks.common.registry.IronTanksItems;

import net.neoforged.bus.api.IEventBus;
import net.neoforged.fml.ModContainer;
import net.neoforged.fml.common.Mod;
import net.neoforged.neoforge.capabilities.Capabilities;
import net.neoforged.neoforge.capabilities.RegisterCapabilitiesEvent;

@Mod(IronTanks.MODID)
public final class IronTanks {
    public static final String MODID = "irontanks";

    public IronTanks(IEventBus modBus, ModContainer modContainer) {
        init(modBus);
        modBus.addListener(this::registerCapabilities);
    }

    private static void init(IEventBus modBus) {
        IronTanksBlocks.register(modBus);
        IronTanksItems.register(modBus);
        IronTanksBlockEntities.register(modBus);
        BCCore.BUILDCRAFT_TAB.addItemProvider(IronTanksItems::getCreativeTabItems);

        // API2 registration is code-owned and must happen before BuildCraft freezes addon content.
        IronTanksGuide.register();
    }

    private void registerCapabilities(RegisterCapabilitiesEvent event) {
        //? if >=1.21.11 {
        event.registerBlockEntity(Capabilities.Fluid.BLOCK, IronTanksBlockEntities.TANK.get(), (tank, side) ->
                TransferInterop.exportFluids(() -> tank.isRemoved() ? null : tank, tank::setChanged));
        event.registerBlockEntity(Capabilities.Fluid.BLOCK, IronTanksBlockEntities.CREATIVE_TANK.get(), (tank, side) ->
                TransferInterop.exportFluids(() -> tank.isRemoved() ? null : tank, tank::setChanged));
        event.registerBlockEntity(Capabilities.Fluid.BLOCK, IronTanksBlockEntities.VOID_TANK.get(), (tank, side) ->
                TransferInterop.exportFluids(() -> tank.isRemoved() ? null : tank, tank::setChanged));
        //? } else {
        /*?
        // BuildCraft API2 discovers these native handlers through its platform fluid bridge.
        event.registerBlockEntity(Capabilities.FluidHandler.BLOCK, IronTanksBlockEntities.TANK.get(), (tank, side) -> tank);
        event.registerBlockEntity(Capabilities.FluidHandler.BLOCK, IronTanksBlockEntities.CREATIVE_TANK.get(), (tank, side) -> tank);
        event.registerBlockEntity(Capabilities.FluidHandler.BLOCK, IronTanksBlockEntities.VOID_TANK.get(), (tank, side) -> tank);
        ?*/
        //? }
    }
}
