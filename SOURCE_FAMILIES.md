# Iron Tanks build generations and source layout

Iron Tanks Community Edition follows the same multi-generation layout used by BuildCraft Community Edition. The repository has three independent Gradle/Stonecutter builds and one layered source tree.

## Build generations

### `legacy`

Targets:

- `1.19.2-forge`
- `1.20.1-forge`

Build root: `builds/legacy`

This generation owns the ForgeGradle targets and has its own Gradle wrapper and Stonecutter controller.

### `modern`

Targets:

- `1.21.1-neoforge`
- `1.21.11-neoforge`

Build root: `builds/modern`

This generation uses a dedicated Gradle 8.8 wrapper and Java 21.

### `26.X`

Targets:

- `26.1.2-neoforge`
- `26.2-neoforge`
- `26.3-neoforge`

Build root: `builds/26.X`

NeoForge targets use Java 25 and Gradle 9.1.0. The modern and 26.X
build scripts share `build-logic/neoforge-target.gradle` to keep packaging,
localization imports, dependency declarations and output layouts identical.

## Repository layout

```text
build-config/
├─ common.properties
└─ generations.properties

builds/
├─ legacy/
├─ modern/
└─ 26.X/

source-shared/
└─ src/                         code/resources valid everywhere

source-families/
├─ legacy/                      Minecraft-generation implementation
├─ modern/
└─ 26.X/                       26.x resources / native API overrides

source-platforms/
├─ forge/                       Forge registration/capability glue
└─ neoforge/                    NeoForge registration/capability glue

version-src/
├─ 1.19.2-forge/
├─ 1.20.1-forge/
├─ 1.21.1-neoforge/             target-only metadata and resources
├─ 1.21.11-neoforge/            client item definitions and migrated recipes
├─ 26.1.2-neoforge/             pack metadata
├─ 26.2-neoforge/               pack metadata
└─ 26.3-neoforge/               pack metadata
```

Each target is materialized as:

```text
shared + family + platform + target overlay = effective target source tree
```

Later layers override the same logical path from earlier layers. The generated tree lives under the target build directory and is never authoritative source.

## Placement rules

- Put common gameplay, API2 integration, models, recipes and textures in `source-shared`.
- Put broad Minecraft-generation differences in `source-families/<generation>`.
- Put loader imports, event buses, registries, capabilities and loader lifecycle code in `source-platforms/<loader>`.
- Put only irreducible target-specific files in `version-src/<target>`; currently this is loader metadata and `pack.mcmeta`.
- Do not reintroduce full per-version source copies.

The 1.19.2 implementation remains the behaviour reference. Source code may differ across generations/loaders, but player-visible Iron Tanks behaviour should remain equivalent.

## Build commands

Build every generation:

```bash
./build-all.sh
```

Windows PowerShell:

```powershell
./build-all.ps1
```

Build only one generation:

```bash
cd builds/legacy
./gradlew buildAndCollect
```

```bash
cd builds/modern
./gradlew buildAndCollect
```

```bash
cd builds/26.X
./gradlew buildAndCollect
```

Run the active target:

```bash
cd builds/legacy
./gradlew runActiveClient
```

```bash
cd builds/modern
./gradlew runActiveClient
```

```bash
cd builds/26.X
./gradlew runActiveClient
```

List targets and validate the architecture:

```bash
python scripts/validate-stonecutter.py --list-targets
python scripts/validate-stonecutter.py
python scripts/validate-source-families.py
python scripts/verify_port.py
```

## BuildCraft dependency

BCCE is a normal remote dependency resolved from Modrinth Maven. The shared configuration pins the BCCE Modrinth project ID, while each target pins its exact version number:

```text
maven.modrinth:z3Aj5eOl:8.0.26+<minecraft>+<loader>
```

Forge targets pass the dependency through `fg.deobf(...)`; NeoForge targets use the normal ModDevGradle `implementation` configuration. No locally staged BCCE jar is required. Each target requires BCCE
`[8.0.24,)` at runtime and builds against `8.0.26`.

## Normal tank contract

Ordinary tiered tanks extend native BCCE `BlockTank` and `TileTank` and only
change storage capacities, material hardness and explosion resistance.
They use the original BuildCraft tank column mechanics (liquid/gas balancing,
compatible-fluid checks, fluid containers, pipe capabilities, GUI/comparator
and persistence). Specialized Void/Creative tiers do not join normal columns;
fluid transactions of the Void tank must not delete normal tank contents.
The shared behavior contract is checked in `scripts/tests/test_tank_parity.py`.
