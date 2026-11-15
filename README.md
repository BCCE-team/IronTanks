# Iron Tanks Community Edition

Unofficial community-maintained port of Iron Tanks for BuildCraft Community Edition, originally developed by Memesis414 for BCCE.

## Supported versions

- Minecraft 1.19.2 — Forge
- Minecraft 1.20.1 — Forge
- Minecraft 1.21.1 — NeoForge
- Minecraft 1.21.11 — NeoForge
- Minecraft 26.1.2 — NeoForge
- Minecraft 26.2 — NeoForge
- Minecraft 26.3 — NeoForge
- Minecraft 26.3 — Fabric

The addon registers its BuildCraft Guide Book content through `buildcraft.api.v2` and uses loader-native fluid capabilities for platform integration.

## Multi-version build architecture

ITCE mirrors BCCE's current build/source architecture:

- **legacy** build generation — 1.19.2 Forge and 1.20.1 Forge;
- **modern** build generation — 1.21.1 and 1.21.11 NeoForge;
- **26.X** build generation — 26.1.2, 26.2, 26.3 NeoForge and 26.3 Fabric

Each generation has an independent Gradle wrapper, Stonecutter controller and target matrix under `builds/legacy`, `builds/modern`, or `builds/26.X`.

Targets are assembled from layered source roots:

```text
source-shared
+ source-families/<generation>
+ source-platforms/<loader>
+ version-src/<target>
```

This keeps common Iron Tanks gameplay in one place while isolating loader registration/capability code and Minecraft-generation differences. See [`SOURCE_FAMILIES.md`](SOURCE_FAMILIES.md) for the full layout and build commands.

## Building

All eight targets now resolve BCCE from **Modrinth Maven** without a local BuildCraft JAR. Forge/NeoForge targets use their existing BCCE 8.0.26 coordinates. Fabric 26.3 pins the supplied Modrinth version ID `XTATlTsu` (project `z3Aj5eOl`). It remains a preview pending a real compile and gameplay smoke test.

```bash
./build-all.sh
```

Or build one generation directly:

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

Every released target pins the matching BCCE artifact (`8.0.26+<minecraft>+<loader>`). Released NeoForge/Forge mod metadata requires **BCCE 8.0.24 or newer**.

### Build the 26.3 Fabric preview

**Java 25**, Gradle 9.8.1 and network access to Modrinth Maven are required. No local BCCE build, path flag or manual JAR installation is necessary for the development compile:

On Windows, install JDK 25 if it is not already installed: `winget install --id EclipseAdoptium.Temurin.25.JDK -e`. The checked-in `builds/26.X/gradle/gradle-daemon-jvm.properties` selects **JDK 25 for the 26.X Gradle daemon**, even when `java -version` in the outer PowerShell session reports Java 21. It does not change the legacy or modern build JVM configuration. Close and reopen the terminal after installing Java 25, then run `./build-all.ps1 assemble` from the repo root. Java 25 must be installed or available through a configured Gradle toolchain; declaring `java.toolchain.languageVersion = 25` alone is not sufficient to load Fabric Loom during Gradle configuration.

```bash
cd /path/to/IronTanks/builds/26.X
./gradlew :26.3-fabric:buildAndCollect
```

The addon resolves `maven.modrinth:z3Aj5eOl:XTATlTsu` through `implementation` and checks that the resolved JAR is a `buildcraftlib` Fabric mod for Minecraft 26.3. The version ID is pinned in `builds/26.X/targets.properties` under `target.26.3-fabric.buildcraft.maven_version`, separate from the in-mod semantic version. If the Modrinth version ID refers to a different loader or Minecraft release, Gradle fails early with a clear error instead of building against an incompatible JAR.

**Fabric 26.3 crafting recipes:** The Fabric target keeps the same 30 shaped recipes
and original inputs/results, but routes alternative glass/common-material tags
through `irontanks:compat/*` item tags. Vanilla glass, panes, copper, iron,
gold, diamonds, emeralds, redstone and black dye remain usable without a
third-party materials mod. Recipes that require silver, aluminium, stainless
steel, titanium or tungsten steel use Fabric resource conditions and are
loaded only when the corresponding conventional item tags are available;
`aluminum`/`aluminium`, `stainlesssteel`/`stainless_steel`, and
`tungstensteel`/`tungsten_steel` alternatives are supported. This prevents
missing-material recipe registry crashes on minimal Fabric installations.
The change is scoped to `version-src/26.3-fabric` and does not alter recipes
for Forge or NeoForge targets.

The produced addon JAR is copied into `build/libs/26.X/3.0.4/` in the Iron Tanks repository root. To run the game/server, install the matching BCCE Fabric JAR and its runtime dependencies (Fabric API and Team Reborn Energy).

The generation-level `buildAndCollect` and top-level `build-all` still build the seven established Forge/NeoForge targets; `buildAllIncludingFabric` includes the Fabric preview. CI compiles Fabric against the same pinned **Modrinth Maven** release, with no separate BCCE checkout. Automatic release publication remains disabled for Fabric pending compile and gameplay smoke-test confirmation.

## Original Iron Tanks normal-tank behavior

The 11 normal tiers (copper through tungstensteel, including obsidian) have **one
and only one difference in fluid gameplay** from the standard BuildCraft tank:
their per-block storage capacity. They extend the native BCCE `BlockTank` and
`TileTank` classes rather than implementing their own transfer engine.

- A vertical stack of compatible normal tiers, or a stack mixed with BuildCraft
  glass tanks, acts as one logical storage column: capacity is the sum of the
  individual capacities. Horizontal adjacency does not merge into one column.
- Water/oil and other liquids settle in the lower tanks; gases fill the top
  tanks first. Each tank still stores its own liquid and persists it to disk.
- Different fluids are not mixed; BCCE's native fluid compatibility and
  balancing determine whether parts of a stack can join.
- Vanilla BuildCraft bucket interactions, GUI, comparator output, fluid-pipe
  compatibility and native capability bridge are all inherited unchanged.
- In-place upgrade items preserve the fluid and block state of the replaced
  tank, without adding additional transfer mechanics.
- Obsidian has higher blast resistance, not a different fluid engine.
- Void and Creative are **special tiers** and do not share their contents with
  regular stacks. They remain independent from the original fluid storage
  behavior; in particular the Void tank cannot consume adjacent tank fluid.

All eight targets have source-contract regression tests in
`scripts/tests/test_tank_parity.py`. These tests do not replace in-game
GameTests or real server/client smoke tests.

## Automatically bundled localizations

UI translations, localized Guide Book page text, and the Guide Book language
index are imported **at build time** from
[`BCCE-team/Localizations`](https://github.com/BCCE-team/Localizations), using
only the `irontanks/` subtree. Translations are embedded in every resulting JAR:
no separate language addon is required. This is the same external-localization
strategy used by BCCE itself.

The canonical English (`en_us`) UI and Guide Book resources remain in
`source-shared`, even if the localization repository provides an English file.
The external `irontanks/guide/languages.json` replaces the English-only index
when packaging, so the Guide Book discovers all translated languages. The
staging script checks malformed/duplicate JSON keys, mismatched language lists,
and the exact JAR contents. All generated files and the cloned translation
cache live in ignored `build/` directories.

Normal online builds automatically find a sibling `Localizations` checkout or
fetch/update the external repository at the selected revision (`main` by
default). CI uses an explicit checkout. Offline builds require a cached Git
checkout or local translations.

Override the source/revision in Gradle when needed:

```bash
cd builds/legacy
./gradlew buildAndCollect -PirontanksLocalizationsDir=../../Localizations
# or: -PirontanksLocalizationsRef=<commit-or-branch>
```

An absolute directory is also supported through the environment variable
`IRONTANKS_LOCALIZATIONS_DIR`. Release builds pin the Git commit SHA of the
translation repository once and reuse it for every target.

## Seamless vertical tank columns

Normal Iron Tanks tiers keep BCCE's native block occlusion and the same
`cullface: up`/`cullface: down` end-cap geometry. Stacking ordinary tanks,
including mixed Iron Tanks and BuildCraft tanks, hides the internal top and
bottom faces while leaving the outer end caps and glass-like side textures
visible. The existing `joined_below` texture variants remove the visible side
seam. Void and Creative tanks do not join normal fluid columns; their end
caps retain non-occluding rendering.

## Automated releases

The separate `.github/workflows/publish.yml` is modeled on BCCE's release
pipeline. **Publishing a GitHub Release** with a tag matching
`common.mod.version` (currently `3.0.4-bcce`) triggers:

1. Source, version, Gradle wrapper, project and token validation.
2. Pinned localization checkout and parallel builds of `legacy`,
   `modern` and `26.X` generations.
3. Verification that all seven released JARs contain the exact external
   translations, Guide Book language index and original English resources.
4. **Sequential** publishing of 1.19.2 Forge, 1.20.1 Forge, 1.21.1 NeoForge,
   1.21.11 NeoForge, 26.1.2 NeoForge, 26.2 NeoForge and 26.3 NeoForge to
   Modrinth, CurseForge and the GitHub Release, with a
   60-second gap between Minecraft versions.

Regular commits/PRs only run `.github/workflows/ci.yml`: they **never publish**.
A failed build/verification blocks publication. Release targets are declared
explicitly and checked against the Stonecutter target matrices. The eighth target (Fabric 26.3) is checked by CI but excluded from publishing.

Before publishing, set these **GitHub Actions repository secrets** under
`Settings → Secrets and variables → Actions`:

- `MODRINTH_TOKEN` — a token with publishing permission for IronTanks.
- `CURSEFORGE_TOKEN` — a token with publishing permission for IronTanks.

The known CurseForge project ID is `1640876`. Modrinth is configured with the
project slug `irontanks-community-edition` from the BCCE download link; the
pipeline checks the project via Modrinth's API before uploading anything.
If its current slug/ID differs, set repository variable `MODRINTH_PROJECT_ID`
to the actual project ID. Required dependency links point to BCCE on both
platforms (`z3Aj5eOl` / `1592400`). `GITHUB_TOKEN` is supplied by GitHub
Actions and requires no extra repository secret.

Do **not** reuse an already published version tag. Update
`common.mod.version`, create the matching tag, and publish its GitHub Release.

## Verification

```bash
python scripts/validate-stonecutter.py
python scripts/validate-source-families.py
python scripts/verify_port.py
python -m unittest discover -s scripts/tests -p test_localization_packaging.py -v
python -m unittest discover -s scripts/tests -p test_tank_parity.py -v
```

Production CI also builds every target and verifies localization bytes inside
each JAR against the checked-out translation repository.

## License

Iron Tanks Community Edition is distributed under the MIT License, preserving the licensing of the original Iron Tanks project. See `LICENSE.txt` and `NOTICE.md`.
