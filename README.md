# Iron Tanks Community Edition

Unofficial community-maintained port of Iron Tanks for BuildCraft Community Edition, originally developed by Memesis414 for BCCE.

## Supported versions

- Minecraft 1.19.2 — Forge
- Minecraft 1.20.1 — Forge
- Minecraft 1.21.1 — NeoForge
- Minecraft 1.21.11 — NeoForge

The addon registers its BuildCraft Guide Book content through `buildcraft.api.v2` and uses loader-native fluid capabilities for platform integration.

## Multi-version build architecture

ITCE mirrors BCCE's current build/source architecture:

- **legacy** build generation — 1.19.2 Forge and 1.20.1 Forge;
- **modern** build generation — 1.21.1 and 1.21.11 NeoForge, with 1.21.11 as the active modern target.

Each generation has an independent Gradle wrapper, Stonecutter controller and target matrix under `builds/legacy` or `builds/modern`.

Targets are assembled from layered source roots:

```text
source-shared
+ source-families/<generation>
+ source-platforms/<loader>
+ version-src/<target>
```

This keeps common Iron Tanks gameplay in one place while isolating loader registration/capability code and Minecraft-generation differences. See [`SOURCE_FAMILIES.md`](SOURCE_FAMILIES.md) for the full layout and build commands.

## Building

BCCE 8.0.21 is resolved directly from Modrinth Maven. No local BuildCraft jars are required.

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

Each target pins the matching BCCE artifact (`8.0.21+<minecraft>+<loader>`) so Forge and NeoForge builds cannot accidentally resolve a jar for another Minecraft version.

## Verification

```bash
python scripts/validate-stonecutter.py
python scripts/validate-source-families.py
python scripts/verify_port.py
```

## License

Iron Tanks Community Edition is distributed under the MIT License, preserving the licensing of the original Iron Tanks project. See `LICENSE.txt` and `NOTICE.md`.
