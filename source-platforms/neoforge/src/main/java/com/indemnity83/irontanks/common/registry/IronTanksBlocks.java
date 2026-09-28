
package com.indemnity83.irontanks.common.registry;

import com.indemnity83.irontanks.IronTanks;
import com.indemnity83.irontanks.common.block.CreativeTankBlock;
import com.indemnity83.irontanks.common.block.StackableTankBlock;
import com.indemnity83.irontanks.common.block.TankBlock;
import com.indemnity83.irontanks.common.block.VoidTankBlock;
import net.minecraft.world.level.block.state.BlockBehaviour;

import net.neoforged.bus.api.IEventBus;
import net.neoforged.neoforge.registries.DeferredRegister;

import java.util.List;
import java.util.function.Function;
import java.util.function.Supplier;

public final class IronTanksBlocks {
    public static final DeferredRegister.Blocks BLOCKS = DeferredRegister.createBlocks(IronTanks.MODID);

    public static final Supplier<StackableTankBlock> COPPER_TANK = registerTank("copper_tank", properties -> new StackableTankBlock(27, 4.0F, 2.0F, properties));
    public static final Supplier<StackableTankBlock> IRON_TANK = registerTank("iron_tank", properties -> new StackableTankBlock(32, 5.0F, 3.0F, properties));
    public static final Supplier<StackableTankBlock> SILVER_TANK = registerTank("silver_tank", properties -> new StackableTankBlock(43, 6.0F, 5.0F, properties));
    public static final Supplier<StackableTankBlock> GOLD_TANK = registerTank("gold_tank", properties -> new StackableTankBlock(48, 7.0F, 4.0F, properties));
    public static final Supplier<StackableTankBlock> DIAMOND_TANK = registerTank("diamond_tank", properties -> new StackableTankBlock(64, 8.0F, 6.0F, properties));
    public static final Supplier<StackableTankBlock> OBSIDIAN_TANK = registerTank("obsidian_tank", properties -> new StackableTankBlock(64, 50.0F, 1_200.0F, properties));
    public static final Supplier<StackableTankBlock> EMERALD_TANK = registerTank("emerald_tank", properties -> new StackableTankBlock(96, 8.0F, 6.0F, properties));
    public static final Supplier<StackableTankBlock> ALUMINIUM_TANK = registerTank("aluminium_tank", properties -> new StackableTankBlock(96, 5.0F, 4.0F, properties));
    public static final Supplier<StackableTankBlock> STAINLESSSTEEL_TANK = registerTank("stainlesssteel_tank", properties -> new StackableTankBlock(128, 9.0F, 8.0F, properties));
    public static final Supplier<StackableTankBlock> TITANIUM_TANK = registerTank("titanium_tank", properties -> new StackableTankBlock(256, 10.0F, 10.0F, properties));
    public static final Supplier<StackableTankBlock> TUNGSTENSTEEL_TANK = registerTank("tungstensteel_tank", properties -> new StackableTankBlock(512, 12.0F, 14.0F, properties));
    public static final Supplier<VoidTankBlock> VOID_TANK = registerTank("void_tank", properties -> new VoidTankBlock(8, 5.0F, 6.0F, properties));
    public static final Supplier<CreativeTankBlock> CREATIVE_TANK = registerTank("creative_tank", properties -> new CreativeTankBlock(1, properties));

    public static final List<Supplier<? extends TankBlock>> NORMAL_TANKS = List.of(
            COPPER_TANK, IRON_TANK, SILVER_TANK, GOLD_TANK, DIAMOND_TANK, OBSIDIAN_TANK,
            EMERALD_TANK, ALUMINIUM_TANK, STAINLESSSTEEL_TANK, TITANIUM_TANK, TUNGSTENSTEEL_TANK
    );

    public static final List<Supplier<? extends TankBlock>> ALL_TANKS = List.of(
            COPPER_TANK, IRON_TANK, SILVER_TANK, GOLD_TANK, DIAMOND_TANK, OBSIDIAN_TANK,
            EMERALD_TANK, ALUMINIUM_TANK, STAINLESSSTEEL_TANK, TITANIUM_TANK, TUNGSTENSTEEL_TANK,
            VOID_TANK, CREATIVE_TANK
    );

    private IronTanksBlocks() {
    }

    private static <T extends TankBlock> Supplier<T> registerTank(String name, Function<BlockBehaviour.Properties, T> factory) {
        //? if >=1.21.11 {
        return BLOCKS.registerBlock(name, factory, TankBlock::createProperties);
        //? } else {
        /*?
        return BLOCKS.registerBlock(name, factory, TankBlock.createProperties());
        ?*/
        //? }
    }

    public static void register(IEventBus bus) {
        BLOCKS.register(bus);
    }
}
