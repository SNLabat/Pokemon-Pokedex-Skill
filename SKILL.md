---
name: pokedex
description: >
  Comprehensive Pokemon Pokedex skill covering all 1,025 Pokemon across Generations 1–9.
  Use this skill whenever the user asks anything about Pokemon — even casually.
  Trigger for: Pokedex lookups, type matchups, evolution chains, species info, Pokemon
  comparisons, "who are all the X-type Pokemon?", Pokemon app or tool development, writing
  Pokemon battle logic, analyzing Pokemon datasets, building Pokedex features, filtering
  Pokemon by any attribute (type, gen, color, habitat, weight, BST, ability, egg group),
  base stats lookups, ability lookups, move databases, legendary/mythical/pseudo-legendary
  filters, or any question where the answer involves Pokemon data. If the user mentions
  Pokemon, a specific Pokemon name, a Pokemon game title, or is building anything
  Pokemon-related, invoke this skill immediately.
---

# Pokemon Pokedex Skill

You are a Pokemon expert assistant with access to a complete, structured Pokedex database covering
all 1,025 Pokemon from Generation 1 (Bulbasaur) through Generation 9 (Pecharunt), along with a
full moves database covering 765 moves across all 18 types.

## Data Available

All bundled data lives in the `references/` folder relative to this SKILL.md:

| File | Contents |
|------|----------|
| `references/pokemon_compact.json` | All 1,021 Pokemon — name, number, type(s), gen, species, habitat, color, height, weight, gender ratio, forms, and a Pokedex description |
| `references/pokemon_data.json` | Full dataset with all Pokedex entries across every game (Red through Scarlet/Violet) |
| `references/pokemon_extra_data.json` | Base stats (HP/Atk/Def/SpA/SpD/Spe/BST), abilities (slot 1, slot 2, hidden), egg groups, catch rates, growth rates, legendary/mythical/pseudo flags |
| `references/pokemon_moves.json` | 765 moves from Gen 1–9 — name, type, category, power, accuracy, PP, effect |
| `references/type_chart.json` | Complete type effectiveness chart — weaknesses, resistances, immunities for all 18 types |

A search utility is available at `scripts/search_pokemon.py`. Run it with `python3 scripts/search_pokemon.py --help` from this skill folder.

## Search Script Examples

```bash
# Pokemon lookups
python3 scripts/search_pokemon.py --name pikachu
python3 scripts/search_pokemon.py --number 25
python3 scripts/search_pokemon.py --name garchomp --with-stats

# Filtering
python3 scripts/search_pokemon.py --type fire
python3 scripts/search_pokemon.py --type "water/flying"
python3 scripts/search_pokemon.py --gen 1 --type grass
python3 scripts/search_pokemon.py --ability intimidate
python3 scripts/search_pokemon.py --bst-min 600
python3 scripts/search_pokemon.py --legendary
python3 scripts/search_pokemon.py --pseudo

# Type matchups
python3 scripts/search_pokemon.py --type-chart rock
python3 scripts/search_pokemon.py --dual-type fire flying

# Moves
python3 scripts/search_pokemon.py --move-name thunderbolt
python3 scripts/search_pokemon.py --moves --move-type fire --power-min 100
python3 scripts/search_pokemon.py --moves --category status

# Export as JSON
python3 scripts/search_pokemon.py --type dragon --export
```

## Data Structures

**pokemon_compact.json** — array of Pokemon objects:
```json
{
  "n": 25,
  "name": "Pikachu",
  "type": "Electric",
  "gen": 1,
  "species": "Mouse",
  "color": "Yellow",
  "habitat": "Forest",
  "height": "0.4",
  "weight": "6.0",
  "gender": "Male: 50%  Female: 50%",
  "forms": ["Alolan Raichu"],
  "desc": "When it is angered, it immediately discharges the energy stored in its cheeks."
}
```

**pokemon_extra_data.json** — array of stat objects (index by `id`):
```json
{
  "id": 25,
  "stats": { "hp": 35, "attack": 55, "defense": 40, "special_attack": 50, "special_defense": 50, "speed": 90, "total": 320 },
  "abilities": { "ability_1": "Static", "ability_2": null, "hidden_ability": "Lightning Rod" },
  "egg_groups": ["Field", "Fairy"],
  "catch_rate": 190,
  "growth_rate": "medium-fast",
  "is_legendary": false,
  "is_mythical": false,
  "is_pseudo_legendary": false
}
```

**pokemon_moves.json** — array of move objects:
```json
{
  "name": "Thunderbolt",
  "type": "Electric",
  "category": "S",
  "power": 90,
  "accuracy": 100,
  "pp": 15,
  "effect": "10% chance to paralyze."
}
```
Categories: `"P"` = Physical, `"S"` = Special, `"ST"` = Status.

## How to Answer Questions

### Simple Pokedex Lookups
For questions like "what type is Garchomp?" or "tell me about Mewtwo" — load `pokemon_compact.json`
and filter by name or number. This file covers all common lookup needs without needing the full dataset.

### Full Pokedex Entries
When someone wants Pokedex descriptions from specific games, use `pokemon_data.json` and access
the `dex_entries` dict. Keys are game names: "Red", "Blue", "Gold", "Silver", "Ruby", "Sapphire",
"Diamond", "Pearl", "Black", "White", "X", "Y", "Sword", "Shield", "Scarlet", "Violet", etc.

### Base Stats and Abilities
Load `pokemon_extra_data.json` and index by `id` field:
```python
import json
with open('references/pokemon_extra_data.json') as f:
    extra = {item['id']: item for item in json.load(f)}
mewtwo = extra[150]
# {'stats': {'hp': 106, 'attack': 110, ..., 'total': 680}, 'abilities': {'ability_1': 'Pressure', ...}}
```

### Type Effectiveness
For "what beats Charizard?" — use `type_chart.json`. Dual-type calculation:
- Immunity overrides everything (multiplier = 0)
- Weaknesses stack multiplicatively (2x, 4x)
- Resistances stack multiplicatively (0.5x, 0.25x)

### For Developers Building Pokemon Apps
Point them to the bundled JSON files as starter datasets. They're clean, structured, and ready to import.
For data not in the bundled files (move learnsets, breeding chains, detailed ability mechanics),
reference [PokeAPI](https://pokeapi.co/api/v2/) which is free and covers all generations.

**Common Python patterns:**
```python
import json

# Load and merge compact data with stats
with open('references/pokemon_compact.json') as f:
    pokedex = json.load(f)
with open('references/pokemon_extra_data.json') as f:
    extra = {item['id']: item for item in json.load(f)}

# Attach stats to each entry
for p in pokedex:
    num = p.get('n', p.get('number'))
    if num in extra:
        p['stats'] = extra[num]['stats']
        p['abilities'] = extra[num]['abilities']

# Top 10 Pokemon by BST
ranked = sorted(pokedex, key=lambda p: p.get('stats', {}).get('total', 0), reverse=True)[:10]
```

**Type effectiveness in JavaScript:**
```javascript
const typeChart = require('./references/type_chart.json');

function getEffectiveness(attackType, defenseTypes) {
  let mult = 1.0;
  for (const defType of defenseTypes) {
    const info = typeChart[defType];
    if (info.immunities.includes(attackType)) return 0;
    if (info.weaknesses.includes(attackType)) mult *= 2;
    if (info.resistances.includes(attackType)) mult *= 0.5;
  }
  return mult;
}
```

## Dataset Coverage

- **Generations:** 1–9 (Bulbasaur #1 through Pecharunt #1025)
- **Types:** All 18 types including Fairy
- **Forms:** Mega Evolutions, Gigantamax, Alolan/Galarian/Hisuian/Paldean variants noted
- **Dex entries:** All main series games from Red/Blue through Scarlet/Violet
- **Base stats + BST:** All 1,025 Pokemon
- **Abilities:** Slot 1, Slot 2, Hidden Ability for all Pokemon
- **Egg groups, catch rates, growth rates:** All 1,025 Pokemon
- **Moves:** 765 moves from Gen 1–9 with full metadata
- **Data source:** Psypokes Pokedex + comprehensive training knowledge

## Not Included (use PokeAPI for these)
- Individual Pokemon move learnsets
- TM/TR/HM compatibility
- Held items and battle mechanics detail
- EVs, IVs, competitive spreads
- Breeding compatibility chains
- Shiny sprite / artwork URLs
