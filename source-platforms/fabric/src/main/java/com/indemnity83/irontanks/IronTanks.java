package com.indemnity83.irontanks;

import buildcraft.core.BCCore;
import buildcraft.lib.platform.storage.FabricStorageLookups;
import com.indemnity83.irontanks.common.guide.IronTanksGuide;
import com.indemnity83.irontanks.common.registry.IronTanksBlockEntities;
import com.indemnity83.irontanks.common.registry.IronTanksBlocks;
import com.indemnity83.irontanks.common.registry.IronTanksItems;
import net.fabricmc.api.ModInitializer;
import net.fabricmc.fabric.api.event.player.UseBlockCallback;
import com.indemnity83.irontanks.common.item.UpgradeItem;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.item.context.UseOnContext;

/** Iron Tanks Fabric 26.3 entrypoint. BuildCraft's fabric initializer runs before this addon. */
public final class IronTanks implements ModInitializer {
    public static final String MODID = "irontanks";

    @Override
    public void onInitialize() {
        // Fabric binds registries immediately. Block entities refer to already-bound blocks.
        IronTanksBlocks.register();
        IronTanksItems.register();
        IronTanksBlockEntities.register();

        // BCCE registers the inherited TileTank fluid handler in Fabric Transfer API.
        // Registered block entities are visible to both native Fabric pipes and BCCE pipes.
        FabricStorageLookups.registerAddonType(IronTanksBlockEntities.TANK.get());
        FabricStorageLookups.registerAddonType(IronTanksBlockEntities.CREATIVE_TANK.get());
        FabricStorageLookups.registerAddonType(IronTanksBlockEntities.VOID_TANK.get());

        // Fabric does not invoke NeoForge's onItemUseFirst. BCCE tanks handle
        // block interaction themselves, before vanilla Item#useOn would run.
        // Intercept only our upgrades before the tank opens its GUI / bucket logic.
        UseBlockCallback.EVENT.register((player, level, hand, hit) -> {
            var stack = player.getItemInHand(hand);
            if (!(stack.getItem() instanceof UpgradeItem upgrade)) return InteractionResult.PASS;
            return upgrade.useOn(new UseOnContext(player, hand, hit));
        });

        BCCore.BUILDCRAFT_TAB.addItemProvider(IronTanksItems::getCreativeTabItems);
        // BCCE seals API2 addon entries at SERVER_STARTING / CLIENT_STARTED.
        IronTanksGuide.register();
    }
}
