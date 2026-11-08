"""Static source-contract tests for original Iron Tanks behavior on every loader/MC target.

These tests intentionally do not emulate Minecraft. They lock the addon to the
native BCCE BlockTank/TileTank stack and ensure ordinary tiers cannot acquire
custom fluid transfer, mixing or void/creative behavior in future ports.
"""
from __future__ import annotations

import json
from pathlib import Path
import re
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from source_layout import load_properties, materialize_target, target_ids
from verify_port import BLOCK_SPECS

PACKAGE = 'com/indemnity83/irontanks'
TARGETS = (
    '1.19.2-forge', '1.20.1-forge',
    '1.21.1-neoforge', '1.21.11-neoforge',
    '26.1.2-neoforge', '26.2-neoforge', '26.3-neoforge',
)
SPECIALS = {'VOID_TANK', 'CREATIVE_TANK'}


class OriginalTankContracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = load_properties()
        cls.tmp = tempfile.TemporaryDirectory(prefix='irontanks-parity-')
        cls.roots = {
            target: materialize_target(target, Path(cls.tmp.name) / target, cls.config)
            for target in TARGETS
        }

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def java(self, target: str, subpath: str) -> str:
        return (self.roots[target] / 'src/main/java' / PACKAGE / subpath).read_text(encoding='utf-8')

    def test_all_seven_pinned_targets_are_independent_builds(self):
        self.assertEqual(tuple(target_ids(self.config)), TARGETS)
        for target in TARGETS:
            with self.subTest(target=target):
                prefix = f'target.{target}.'
                self.assertEqual(self.config[prefix+'buildcraft.version'],
                                 '8.0.26+' + target.replace('-', '+'))
                self.assertEqual(self.config[prefix+'buildcraft.version_range'], '[8.0.24,)')
                if target.startswith('26.'):
                    self.assertEqual(self.config[prefix+'java.version'], '25')
                    self.assertEqual(self.config[prefix+'source.family'], '26.X')
                    self.assertEqual(self.config[prefix+'deps.minecraft'], target.split('-')[0])

    def test_all_normal_tank_tiles_use_native_buildcraft_storage_and_physics(self):
        inherited_methods = ('update', 'fill', 'drain', 'balanceTankFluids',
                             'getConnectedTanks', 'canConnectTo', 'onActivated',
                             'getTankCapacity', 'getFluidInTank')
        for target in TARGETS:
            with self.subTest(target=target):
                java = self.java(target, 'common/blockentity/TankTile.java')
                self.assertIn('class TankTile extends TileTank', java)
                self.assertRegex(java, r'super\(type,\s*capacityMb,\s*pos,\s*state\)')
                self.assertIn('tankBlock.getCapacityMb()', java)
                for method in inherited_methods:
                    self.assertNotRegex(java, rf'\b(?:void|boolean|int|FluidStack|List<.*>)\s+{method}\s*\(')

    def test_every_normal_tier_registers_plain_buildcraft_stackable_tank(self):
        for target in TARGETS:
            with self.subTest(target=target):
                java = self.java(target, 'common/registry/IronTanksBlocks.java')
                normal = re.search(r'NORMAL_TANKS\s*=\s*List\.of\((.*?)\);', java, flags=re.S)
                self.assertIsNotNone(normal)
                normal_fields = set(re.findall(r'\b[A-Z_]+_TANK\b', normal.group(1)))
                self.assertEqual(normal_fields, set(BLOCK_SPECS) - SPECIALS)
                for name in normal_fields:
                    self.assertIn('new StackableTankBlock(', java[java.index(name+' ='):].split(';',1)[0])
                for special in SPECIALS:
                    self.assertNotIn(special, normal.group(1))

    def test_original_tank_properties_and_capacity_units_are_not_changed(self):
        for target in TARGETS:
            with self.subTest(target=target):
                stackable = self.java(target, 'common/block/StackableTankBlock.java')
                block = self.java(target, 'common/block/TankBlock.java')
                self.assertIn('extends BlockTank', block)
                self.assertIn('implements ITankBlockConnector', stackable)
                self.assertIn('capacityBuckets * MILLIBUCKETS_PER_BUCKET', block)
                self.assertIn('MILLIBUCKETS_PER_BUCKET = 1_000', block)
                self.assertIn('new TankTile(pos, state, getCapacityMb())', block)
                self.assertIn('properties.strength(hardness, resistance)', block)
                self.assertNotRegex(block, r'\b(?:fill|drain|update|balanceTankFluids)\s*\(')

    def test_end_caps_cull_at_vertical_buildcraft_tank_joints(self):
        # BCCE's tank uses an occluding block and cullface-tagged end caps.
        # An addon that calls noOcclusion() on its normal tank block disables
        # this native adjacent-face optimization and leaves visible internal caps.
        models = ROOT / 'source-shared/src/main/resources/assets/irontanks/models/block'
        base = json.loads((models / 'tank_base.json').read_text(encoding='utf-8'))
        element, = base['elements']
        self.assertEqual(element['from'], [2, 0, 2])
        self.assertEqual(element['to'], [14, 16, 14])
        self.assertEqual(base['render_type'], 'cutout')
        for direction in ('up', 'down'):
            self.assertEqual(element['faces'][direction]['cullface'], direction)
        for direction in ('north', 'south', 'west', 'east'):
            self.assertNotIn('cullface', element['faces'][direction])

        for name in (set(BLOCK_SPECS) - SPECIALS):
            stem = name.lower()
            for variant in ('', '_joined_below'):
                with self.subTest(model=stem+variant):
                    tier = json.loads((models / (stem+variant+'.json')).read_text(encoding='utf-8'))
                    self.assertEqual(tier['parent'], 'irontanks:block/tank_base')

        for target in TARGETS:
            with self.subTest(target=target):
                normal = self.java(target, 'common/block/TankBlock.java')
                self.assertIn('extends BlockTank', normal)
                self.assertIn('super(properties.strength(hardness, resistance).requiresCorrectToolForDrops());', normal)
                self.assertNotRegex(normal, r'super\(properties\.strength\(hardness, resistance\).*?\.noOcclusion\(')
                for name in ('Void', 'Creative'):
                    special = self.java(target, f'common/block/{name}TankBlock.java')
                    self.assertIn('createProperties().noOcclusion()', special)
                    self.assertIn('properties.noOcclusion()', special)

    def test_stackable_tank_end_caps_follow_buildcraft_column_join_state(self):
        # A model cullface is not by itself a reliable seam contract for every
        # translucent tank tier. The renderer must skip *both* vertical caps
        # when the upper tank's BCCE JOINED_BELOW state declares a real joint.
        for target in TARGETS:
            with self.subTest(target=target):
                stackable = self.java(target, 'common/block/StackableTankBlock.java')
                self.assertIn('implements ITankBlockConnector', stackable)
                self.assertIn('boolean skipRendering(BlockState state, BlockState other, Direction side)', stackable)
                self.assertIn('other.getBlock() instanceof ITankBlockConnector', stackable)
                self.assertRegex(stackable, r'side == Direction\.DOWN\s*&& joinsTankBelow\(state\)')
                self.assertRegex(stackable, r'side == Direction\.UP\s*&& joinsTankBelow\(other\)')
                self.assertIn('return super.skipRendering(state, other, side);', stackable)
                self.assertIn('getStateDefinition().getProperty("joined_below")', stackable)
                self.assertNotIn('buildcraft.lib.internal', stackable)

        # Creative/void tanks are deliberately non-connectors; do not hide
        # their end caps even when physically adjacent to ordinary tanks.
        for name in ('VoidTankBlock', 'CreativeTankBlock'):
            src = (ROOT / 'source-shared/src/main/java' / PACKAGE / 'common/block' / (name+'.java')).read_text(encoding='utf-8')
            self.assertIn('extends TankBlock', src)
            self.assertNotIn('implements ITankBlockConnector', src)

    def test_in_world_upgrades_preserve_existing_fluids(self):
        for target in TARGETS:
            with self.subTest(target=target):
                java = self.java(target, 'common/item/UpgradeItem.java')
                self.assertIn('oldTank.tank.getFluid().copy()', java)
                self.assertIn('copySharedProperties(oldState, toBlock.defaultBlockState())', java)
                self.assertIn('newTank.tank.setFluid(fluid)', java)
                self.assertIn('newTank.balanceTankFluids()', java)
                self.assertIn('newTank.sendNetworkUpdate(', java)
                self.assertIn('level.setBlock(pos, oldState, Block.UPDATE_ALL)', java)
                self.assertGreater(java.index('heldStack.shrink(1)'), java.index('newTank.tank.setFluid(fluid)'))
                self.assertIn('Block.UPDATE_ALL', java)

    def test_special_tanks_cannot_share_void_or_creative_fluid_with_column(self):
        for target in TARGETS:
            with self.subTest(target=target):
                for kind in ('Void', 'Creative'):
                    src = self.java(target, f'common/blockentity/{kind}TankTile.java')
                    self.assertRegex(src, r'boolean\s+canConnectTo\(TileTank\s+other,\s*Direction\s+direction\)\s*\{\s*return false;')
                self.assertIn('TRANSFER_PER_TICK = 80', self.java(target, 'common/blockentity/VoidTankTile.java'))
                self.assertIn('FluidAction.SIMULATE', self.java(target, 'common/blockentity/CreativeTankTile.java'))
                self.assertNotIn('extends StackableTankBlock', self.java(target, 'common/block/VoidTankBlock.java'))

    def test_neoforge_fluid_action_is_inherited_from_buildcraft_tank(self):
        # NeoForge 26.3 removed its legacy IFluidHandler. BCCE keeps the
        # FluidAction contract on TileTank's inherited fluid-handler interface.
        # Directly importing NeoForge's old nested enum breaks 26.3 compilation.
        old_import = 'import net.neoforged.neoforge.fluids.capability.IFluidHandler.FluidAction;'
        for target in TARGETS:
            if not target.endswith('-neoforge'):
                continue
            for kind in ('Void', 'Creative'):
                with self.subTest(target=target, tank=kind):
                    src = self.java(target, f'common/blockentity/{kind}TankTile.java')
                    self.assertIn(f'class {kind}TankTile extends TankTile', src)
                    self.assertIn('FluidAction.', src)
                    self.assertNotIn(old_import, src)

    def test_all_seven_use_correct_platform_fluid_capabilities(self):
        for target in TARGETS:
            with self.subTest(target=target):
                mod = self.java(target, 'IronTanks.java')
                reg = self.java(target, 'common/registry/IronTanksBlockEntities.java')
                self.assertIn('normalTankBlocks()', reg)
                if target.startswith('1.19.') or target.startswith('1.20.'):
                    # Forge inherits its fluid handler from BCCE TileTank; unlike
                    # NeoForge there is no explicit block-entity capability event.
                    self.assertIn('BlockEntityType.Builder.of(TankTile::new', reg)
                    self.assertIn('IronTanksBlockEntities.register(modBus)', mod)
                elif target == '1.21.1-neoforge':
                    self.assertIn('IronTanksBlockEntities.TANK.get()', mod)
                    self.assertIn('IronTanksBlockEntities.VOID_TANK.get()', mod)
                    self.assertIn('Capabilities.FluidHandler.BLOCK', mod)
                else:
                    self.assertIn('IronTanksBlockEntities.TANK.get()', mod)
                    self.assertIn('IronTanksBlockEntities.VOID_TANK.get()', mod)
                    self.assertIn('Capabilities.Fluid.BLOCK', mod)
                    self.assertIn('TransferInterop.exportFluids(', mod)

    def test_26x_resources_pack_and_items_are_complete(self):
        for target in TARGETS[-3:]:
            with self.subTest(target=target):
                root = self.roots[target] / 'src/main/resources'
                self.assertTrue((root/'META-INF/neoforge.mods.toml').is_file())
                pack = json.loads((root/'pack.mcmeta').read_text(encoding='utf-8'))['pack']
                prefix = f'target.{target}.'
                self.assertEqual(float(pack['pack_format']), float(self.config[prefix+'pack.format']))
                self.assertEqual(float(pack['forge:data_pack_format']), float(self.config[prefix+'pack.data_format']))
                items = list((root/'assets/irontanks/items').glob('*.json'))
                recipes = list((root/'data/irontanks/recipe').glob('*.json'))
                loot = list((root/'data/irontanks/loot_table/blocks').glob('*.json'))
                self.assertEqual(len(recipes), 30)
                self.assertEqual(len(items), len(list((root/'assets/irontanks/models/item').glob('*.json'))))
                self.assertEqual(len(loot), len(BLOCK_SPECS))
                self.assertTrue((root/'data/minecraft/tags/block/mineable/pickaxe.json').is_file())

    def test_26x_can_be_preprocessed_without_remnants_or_legacy_chat_format(self):
        for target in TARGETS[-3:]:
            with self.subTest(target=target):
                roots = list((self.roots[target]/'src/main/java').rglob('*.java'))
                self.assertEqual(len(roots), 14)
                for java_file in roots:
                    data = java_file.read_text(encoding='utf-8')
                    self.assertNotIn('//? ', data)
                    self.assertNotIn('import net.minecraft.ChatFormatting;', data)
                upgrade = self.java(target, 'common/item/UpgradeItem.java')
                self.assertNotRegex(upgrade, r'@Override\s+public InteractionResult onItemUseFirst')
                self.assertIn('public InteractionResult useOn(', upgrade)

    def test_release_ci_and_toolchains_cover_new_targets(self):
        ci = (ROOT/'.github/workflows/ci.yml').read_text(encoding='utf-8')
        publish = (ROOT/'.github/workflows/publish.yml').read_text(encoding='utf-8')
        gradle26 = (ROOT/'builds/26.X/gradle/wrapper/gradle-wrapper.properties').read_text(encoding='utf-8')
        self.assertIn('gradle-9.1.0-bin.zip', gradle26)
        self.assertIn("id 'net.neoforged.moddev' version '2.0.148'",(ROOT/'builds/26.X/build.neoforge.gradle').read_text(encoding='utf-8'))
        self.assertIn("java: '25'", ci)
        self.assertIn("java: '25'", publish)
        self.assertIn('test_tank_parity.py', ci)
        self.assertIn('test_tank_parity.py', publish)
        for target in TARGETS[-3:]:
            self.assertIn('Publish '+target.split('-')[0]+' NeoForge', publish)
        self.assertEqual(publish.count('uses: Kira-NT/mc-publish@v3'), len(TARGETS))


if __name__ == '__main__':
    unittest.main()
