package com.indemnity83.irontanks.common.registry;

import buildcraft.factory.BCFactoryBlocks;
import buildcraft.lib.compat.RegistryCompat;
import buildcraft.lib.platform.registry.BCDeferredRegister;
import buildcraft.lib.platform.registry.BCRegistryEntry;
import buildcraft.lib.platform.registry.RegistryBinding;
import com.indemnity83.irontanks.IronTanks;
import com.indemnity83.irontanks.common.block.TankBlock;
import com.indemnity83.irontanks.common.item.UpgradeItem;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.item.component.TooltipDisplay;
import net.minecraft.world.level.block.Block;

import java.util.List;
import java.util.function.Consumer;
import java.util.function.Supplier;

public final class IronTanksItems {
    private static final BCDeferredRegister<Item> ITEMS = BCDeferredRegister.create("minecraft:item", IronTanks.MODID);

    public static final BCRegistryEntry<BlockItem> COPPER_TANK = blockItem("copper_tank", IronTanksBlocks.COPPER_TANK);
    public static final BCRegistryEntry<BlockItem> IRON_TANK = blockItem("iron_tank", IronTanksBlocks.IRON_TANK);
    public static final BCRegistryEntry<BlockItem> SILVER_TANK = blockItem("silver_tank", IronTanksBlocks.SILVER_TANK);
    public static final BCRegistryEntry<BlockItem> GOLD_TANK = blockItem("gold_tank", IronTanksBlocks.GOLD_TANK);
    public static final BCRegistryEntry<BlockItem> DIAMOND_TANK = blockItem("diamond_tank", IronTanksBlocks.DIAMOND_TANK);
    public static final BCRegistryEntry<BlockItem> OBSIDIAN_TANK = blockItem("obsidian_tank", IronTanksBlocks.OBSIDIAN_TANK);
    public static final BCRegistryEntry<BlockItem> EMERALD_TANK = blockItem("emerald_tank", IronTanksBlocks.EMERALD_TANK);
    public static final BCRegistryEntry<BlockItem> ALUMINIUM_TANK = blockItem("aluminium_tank", IronTanksBlocks.ALUMINIUM_TANK);
    public static final BCRegistryEntry<BlockItem> STAINLESSSTEEL_TANK = blockItem("stainlesssteel_tank", IronTanksBlocks.STAINLESSSTEEL_TANK);
    public static final BCRegistryEntry<BlockItem> TITANIUM_TANK = blockItem("titanium_tank", IronTanksBlocks.TITANIUM_TANK);
    public static final BCRegistryEntry<BlockItem> TUNGSTENSTEEL_TANK = blockItem("tungstensteel_tank", IronTanksBlocks.TUNGSTENSTEEL_TANK);
    public static final BCRegistryEntry<BlockItem> VOID_TANK = blockItem("void_tank", IronTanksBlocks.VOID_TANK);
    public static final BCRegistryEntry<BlockItem> CREATIVE_TANK = blockItem("creative_tank", IronTanksBlocks.CREATIVE_TANK);

    public static final BCRegistryEntry<UpgradeItem> COPPER_IRON_UPGRADE = upgrade("copper_iron_upgrade", IronTanksBlocks.COPPER_TANK, IronTanksBlocks.IRON_TANK);
    public static final BCRegistryEntry<UpgradeItem> COPPER_SILVER_UPGRADE = upgrade("copper_silver_upgrade", IronTanksBlocks.COPPER_TANK, IronTanksBlocks.SILVER_TANK);
    public static final BCRegistryEntry<UpgradeItem> DIAMOND_OBSIDIAN_UPGRADE = upgrade("diamond_obsidian_upgrade", IronTanksBlocks.DIAMOND_TANK, IronTanksBlocks.OBSIDIAN_TANK);
    public static final BCRegistryEntry<UpgradeItem> GLASS_COPPER_UPGRADE = upgrade("glass_copper_upgrade", BCFactoryBlocks.TANK_BLOCK, IronTanksBlocks.COPPER_TANK);
    public static final BCRegistryEntry<UpgradeItem> GLASS_IRON_UPGRADE = upgrade("glass_iron_upgrade", BCFactoryBlocks.TANK_BLOCK, IronTanksBlocks.IRON_TANK);
    public static final BCRegistryEntry<UpgradeItem> GOLD_DIAMOND_UPGRADE = upgrade("gold_diamond_upgrade", IronTanksBlocks.GOLD_TANK, IronTanksBlocks.DIAMOND_TANK);
    public static final BCRegistryEntry<UpgradeItem> IRON_GOLD_UPGRADE = upgrade("iron_gold_upgrade", IronTanksBlocks.IRON_TANK, IronTanksBlocks.GOLD_TANK);
    public static final BCRegistryEntry<UpgradeItem> SILVER_GOLD_UPGRADE = upgrade("silver_gold_upgrade", IronTanksBlocks.SILVER_TANK, IronTanksBlocks.GOLD_TANK);
    public static final BCRegistryEntry<UpgradeItem> DIAMOND_EMERALD_UPGRADE = upgrade("diamond_emerald_upgrade", IronTanksBlocks.DIAMOND_TANK, IronTanksBlocks.EMERALD_TANK);
    public static final BCRegistryEntry<UpgradeItem> DIAMOND_ALUMINIUM_UPGRADE = upgrade("diamond_aluminium_upgrade", IronTanksBlocks.DIAMOND_TANK, IronTanksBlocks.ALUMINIUM_TANK);
    public static final BCRegistryEntry<UpgradeItem> EMERALD_STAINLESSSTEEL_UPGRADE = upgrade("emerald_stainlesssteel_upgrade", IronTanksBlocks.EMERALD_TANK, IronTanksBlocks.STAINLESSSTEEL_TANK);
    public static final BCRegistryEntry<UpgradeItem> ALUMINIUM_STAINLESSSTEEL_UPGRADE = upgrade("aluminium_stainlesssteel_upgrade", IronTanksBlocks.ALUMINIUM_TANK, IronTanksBlocks.STAINLESSSTEEL_TANK);
    public static final BCRegistryEntry<UpgradeItem> STAINLESSSTEEL_TITANIUM_UPGRADE = upgrade("stainlesssteel_titanium_upgrade", IronTanksBlocks.STAINLESSSTEEL_TANK, IronTanksBlocks.TITANIUM_TANK);
    public static final BCRegistryEntry<UpgradeItem> TITANIUM_TUNGSTENSTEEL_UPGRADE = upgrade("titanium_tungstensteel_upgrade", IronTanksBlocks.TITANIUM_TANK, IronTanksBlocks.TUNGSTENSTEEL_TANK);

    private static final List<Supplier<? extends Item>> CREATIVE_ITEMS = List.of(
        COPPER_TANK, IRON_TANK, SILVER_TANK, GOLD_TANK, DIAMOND_TANK, OBSIDIAN_TANK,
        EMERALD_TANK, ALUMINIUM_TANK, STAINLESSSTEEL_TANK, TITANIUM_TANK, TUNGSTENSTEEL_TANK,
        VOID_TANK, CREATIVE_TANK,
        GLASS_COPPER_UPGRADE, GLASS_IRON_UPGRADE, COPPER_IRON_UPGRADE, COPPER_SILVER_UPGRADE,
        IRON_GOLD_UPGRADE, SILVER_GOLD_UPGRADE, GOLD_DIAMOND_UPGRADE,
        DIAMOND_OBSIDIAN_UPGRADE, DIAMOND_EMERALD_UPGRADE, DIAMOND_ALUMINIUM_UPGRADE,
        EMERALD_STAINLESSSTEEL_UPGRADE, ALUMINIUM_STAINLESSSTEEL_UPGRADE,
        STAINLESSSTEEL_TITANIUM_UPGRADE, TITANIUM_TUNGSTENSTEEL_UPGRADE
    );

    private IronTanksItems() {}

    private static BCRegistryEntry<BlockItem> blockItem(String name, Supplier<? extends TankBlock> block) {
        return RegistryCompat.registerItem(ITEMS, name, () -> new TankBlockItem(block.get(),
            RegistryCompat.itemProperties(new Item.Properties()).useBlockDescriptionPrefix()));
    }

    private static BCRegistryEntry<UpgradeItem> upgrade(String name, Supplier<? extends Block> from,
                                                        Supplier<? extends Block> to) {
        return RegistryCompat.registerItem(ITEMS, name,
            () -> new UpgradeItem(RegistryCompat.itemProperties(new Item.Properties()), from, to));
    }

    public static List<ItemStack> getCreativeTabItems() {
        return CREATIVE_ITEMS.stream().map(Supplier::get).map(ItemStack::new).toList();
    }

    public static void register() {
        ITEMS.register(RegistryBinding.direct());
    }

    private static final class TankBlockItem extends BlockItem {
        private final TankBlock tankBlock;

        private TankBlockItem(TankBlock block, Properties properties) {
            super(block, properties);
            this.tankBlock = block;
        }

        @Override
        public void appendHoverText(ItemStack stack, Item.TooltipContext context, TooltipDisplay display,
                                    Consumer<Component> tooltip, TooltipFlag flag) {
            super.appendHoverText(stack, context, display, tooltip, flag);
            tankBlock.appendTankTooltip(tooltip);
        }
    }
}
