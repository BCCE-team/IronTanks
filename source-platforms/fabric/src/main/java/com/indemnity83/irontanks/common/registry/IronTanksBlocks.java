package com.indemnity83.irontanks.common.registry;

import buildcraft.lib.compat.RegistryCompat;
import buildcraft.lib.platform.registry.BCDeferredRegister;
import buildcraft.lib.platform.registry.BCRegistryEntry;
import buildcraft.lib.platform.registry.RegistryBinding;
import com.indemnity83.irontanks.IronTanks;
import com.indemnity83.irontanks.common.block.CreativeTankBlock;
import com.indemnity83.irontanks.common.block.StackableTankBlock;
import com.indemnity83.irontanks.common.block.TankBlock;
import com.indemnity83.irontanks.common.block.VoidTankBlock;
import net.minecraft.world.level.block.Block;

import java.util.List;
import java.util.function.Supplier;

/** Fabric-native ordered block descriptors; ids are stamped before construction. */
public final class IronTanksBlocks {
    private static final BCDeferredRegister<Block> BLOCKS = BCDeferredRegister.create("minecraft:block", IronTanks.MODID);

    public static final BCRegistryEntry<StackableTankBlock> COPPER_TANK = registerTank("copper_tank", () -> new StackableTankBlock(27, 4.0F, 2.0F));
    public static final BCRegistryEntry<StackableTankBlock> IRON_TANK = registerTank("iron_tank", () -> new StackableTankBlock(32, 5.0F, 3.0F));
    public static final BCRegistryEntry<StackableTankBlock> SILVER_TANK = registerTank("silver_tank", () -> new StackableTankBlock(43, 6.0F, 5.0F));
    public static final BCRegistryEntry<StackableTankBlock> GOLD_TANK = registerTank("gold_tank", () -> new StackableTankBlock(48, 7.0F, 4.0F));
    public static final BCRegistryEntry<StackableTankBlock> DIAMOND_TANK = registerTank("diamond_tank", () -> new StackableTankBlock(64, 8.0F, 6.0F));
    public static final BCRegistryEntry<StackableTankBlock> OBSIDIAN_TANK = registerTank("obsidian_tank", () -> new StackableTankBlock(64, 50.0F, 1_200.0F));
    public static final BCRegistryEntry<StackableTankBlock> EMERALD_TANK = registerTank("emerald_tank", () -> new StackableTankBlock(96, 8.0F, 6.0F));
    public static final BCRegistryEntry<StackableTankBlock> ALUMINIUM_TANK = registerTank("aluminium_tank", () -> new StackableTankBlock(96, 5.0F, 4.0F));
    public static final BCRegistryEntry<StackableTankBlock> STAINLESSSTEEL_TANK = registerTank("stainlesssteel_tank", () -> new StackableTankBlock(128, 9.0F, 8.0F));
    public static final BCRegistryEntry<StackableTankBlock> TITANIUM_TANK = registerTank("titanium_tank", () -> new StackableTankBlock(256, 10.0F, 10.0F));
    public static final BCRegistryEntry<StackableTankBlock> TUNGSTENSTEEL_TANK = registerTank("tungstensteel_tank", () -> new StackableTankBlock(512, 12.0F, 14.0F));
    public static final BCRegistryEntry<VoidTankBlock> VOID_TANK = registerTank("void_tank", () -> new VoidTankBlock(8, 5.0F, 6.0F));
    public static final BCRegistryEntry<CreativeTankBlock> CREATIVE_TANK = registerTank("creative_tank", () -> new CreativeTankBlock(1));

    public static final List<Supplier<? extends TankBlock>> NORMAL_TANKS = List.of(
        COPPER_TANK, IRON_TANK, SILVER_TANK, GOLD_TANK, DIAMOND_TANK, OBSIDIAN_TANK,
        EMERALD_TANK, ALUMINIUM_TANK, STAINLESSSTEEL_TANK, TITANIUM_TANK, TUNGSTENSTEEL_TANK
    );

    public static final List<Supplier<? extends TankBlock>> ALL_TANKS = List.of(
        COPPER_TANK, IRON_TANK, SILVER_TANK, GOLD_TANK, DIAMOND_TANK, OBSIDIAN_TANK,
        EMERALD_TANK, ALUMINIUM_TANK, STAINLESSSTEEL_TANK, TITANIUM_TANK, TUNGSTENSTEEL_TANK,
        VOID_TANK, CREATIVE_TANK
    );

    private IronTanksBlocks() {}

    private static <T extends TankBlock> BCRegistryEntry<T> registerTank(String name, Supplier<T> constructor) {
        // RegistryCompat supplies the 26.3 ResourceKey to the block properties.
        return RegistryCompat.registerBlock(BLOCKS, name, constructor);
    }

    public static void register() {
        BLOCKS.register(RegistryBinding.direct());
    }
}
