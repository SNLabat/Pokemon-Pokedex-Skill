# Pokemon Pokedex — Claude Skill

A comprehensive Pokemon Pokedex Skill for Claude. Covers all 1,025 Pokemon across Generations 1–9
with full base stats, abilities, moves, type matchups, species data, and Pokedex entries from every main
series game.

## Features

- Complete Pokedex for Generations 1–9 (Bulbasaur through Pecharunt)
- Base stats (HP, Atk, Def, SpA, SpD, Spe, BST) for all 1,025 Pokemon
- Abilities (Slot 1, Slot 2, Hidden) for every Pokemon
- 765 moves from Gen 1–9 with type, category, power, accuracy, PP, and effect descriptions
- Full type effectiveness chart for all 18 types including dual-type calculations
- Legendary, mythical, and pseudo-legendary flags
- Egg groups, catch rates, growth rates
- Pokedex entries from every game (Red/Blue through Scarlet/Violet)
- A command-line search utility for fast data queries

## Installation

### 1. Clone or download this repository

```bash
git clone https://github.com/your-username/pokemon-pokedex-skill.git
```

### 2. Place the skill in your Claude skills directory

Copy the `pokedex/` folder into your Claude skills directory:

```
~/.claude/skills/pokedex/
```

Your directory should look like this:

```
~/.claude/skills/pokedex/
├── SKILL.md
├── references/
│   ├── pokemon_compact.json
│   ├── pokemon_data.json
│   ├── pokemon_extra_data.json
│   ├── pokemon_moves.json
│   └── type_chart.json
└── scripts/
    └── search_pokemon.py
```

### 3. Confirm the skill is loaded

Once the skill is in place, Claude will automatically use it when you ask Pokemon-related questions. No additional configuration is required.

## Usage

Claude will pick up the Pokedex skill automatically when Pokemon topics come up. Just ask naturally.

### What you can ask

- "What type is Garchomp and what are its base stats?"
- "Which Pokemon from Gen 1 are pure Fire type?"
- "What are Mewtwo's abilities and catch rate?"
- "Show me all Dragon/Flying type Pokemon"
- "What are the strongest Fire-type special moves?"
- "What beats Steel/Fairy dual type?"
- "List all pseudo-legendary Pokemon"
- "Write me a Python script to load and filter the Pokedex by BST"
- "Build a type effectiveness calculator in JavaScript"
- "Which legendary Pokemon have the highest Speed stat?"

### Command-line search utility

The skill includes `scripts/search_pokemon.py` for direct data queries without going through Claude:

```bash
# From inside the pokedex/ directory:
python3 scripts/search_pokemon.py --name charizard --with-stats
python3 scripts/search_pokemon.py --type fire --gen 1
python3 scripts/search_pokemon.py --pseudo
python3 scripts/search_pokemon.py --bst-min 600
python3 scripts/search_pokemon.py --dual-type water flying
python3 scripts/search_pokemon.py --moves --move-type electric --power-min 90
python3 scripts/search_pokemon.py --ability intimidate
python3 scripts/search_pokemon.py --stats
```

## Bundled Data Files

| File | Description | Size |
|------|-------------|------|
| `references/pokemon_compact.json` | Core Pokedex — all 1,021 Pokemon with type, gen, species, habitat, height, weight, and a description | ~282KB |
| `references/pokemon_data.json` | Full Pokedex with all game-specific Pokedex entries | ~1.5MB |
| `references/pokemon_extra_data.json` | Base stats, abilities, egg groups, catch rates, growth rates, legendary flags | ~476KB |
| `references/pokemon_moves.json` | 765 moves from Gen 1–9 | ~139KB |
| `references/type_chart.json` | Complete type matchup chart for all 18 types | ~3.5KB |

Data sources: Psypokes Pokedex (PDF), augmented from training knowledge for stats, abilities, and moves.

## What's Not Included

For data not in the bundled files, Claude will direct you to
[PokeAPI](https://pokeapi.co/api/v2/) (free, no auth required):

- Individual Pokemon move learnsets
- TM/TR/HM compatibility lists
- Breeding compatibility chains
- Held item details
- Competitive EV spreads and natures

## Skill Structure

```
pokedex/
├── SKILL.md                 # Skill instructions and reasoning examples for Claude
├── references/              # Bundled JSON data files
│   ├── pokemon_compact.json
│   ├── pokemon_data.json
│   ├── pokemon_extra_data.json
│   ├── pokemon_moves.json
│   └── type_chart.json
└── scripts/
    └── search_pokemon.py    # CLI search utility
```

## License

MIT
