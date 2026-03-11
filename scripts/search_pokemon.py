#!/usr/bin/env python3
"""
Pokemon Pokedex Search Utility
Provides fast lookup and filtering of Pokemon data from the bundled JSON.

Usage:
  python search_pokemon.py --name pikachu
  python search_pokemon.py --number 25
  python search_pokemon.py --type electric
  python search_pokemon.py --type "electric/steel"
  python search_pokemon.py --gen 1 --type fire
  python search_pokemon.py --color yellow
  python search_pokemon.py --habitat forest
  python search_pokemon.py --species mouse
  python search_pokemon.py --type-chart electric
  python search_pokemon.py --dual-type fire flying
  python search_pokemon.py --stats            # summary stats
  python search_pokemon.py --export --type water --gen 1
  python search_pokemon.py --name pikachu --with-stats  # include base stats
  python search_pokemon.py --moves --type electric      # search moves by type
  python search_pokemon.py --move-name thunderbolt      # look up a specific move
  python search_pokemon.py --ability intimidate         # find Pokemon with ability
  python search_pokemon.py --legendary                  # list all legendaries
  python search_pokemon.py --pseudo                     # list pseudo-legendaries
  python search_pokemon.py --bst-min 600               # filter by min BST
"""

import json
import sys
import os
import argparse

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REFS_DIR = os.path.join(SCRIPT_DIR, '..', 'references')

def load_data(full=False):
    filename = 'pokemon_data.json' if full else 'pokemon_compact.json'
    path = os.path.join(REFS_DIR, filename)
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_type_chart():
    path = os.path.join(REFS_DIR, 'type_chart.json')
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_extra_data():
    path = os.path.join(REFS_DIR, 'pokemon_extra_data.json')
    with open(path, 'r', encoding='utf-8') as f:
        raw = json.load(f)
    # Build a dict keyed by id for fast lookup
    if isinstance(raw, list):
        return {str(item['id']): item for item in raw}
    return raw

def load_moves():
    path = os.path.join(REFS_DIR, 'pokemon_moves.json')
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_extra(extra_data, number):
    """Look up extra data by Pokedex number."""
    key = str(number)
    return extra_data.get(key)

def search_by_name(data, query):
    q = query.lower()
    return [p for p in data if q in p['name'].lower()]

def search_by_number(data, number):
    return [p for p in data if p.get('n', p.get('number')) == int(number)]

def search_by_type(data, type_query):
    """Match single or dual type. e.g. 'fire', 'fire/flying', 'fire/flying' (order insensitive)."""
    parts = [t.strip().capitalize() for t in type_query.split('/')]
    results = []
    for p in data:
        pokemon_types = [t.strip() for t in p['type'].split('/')]
        if len(parts) == 1:
            if parts[0] in pokemon_types:
                results.append(p)
        else:
            # Both types must match (order insensitive)
            if set(parts) == set(pokemon_types):
                results.append(p)
    return results

def search_by_gen(data, gen):
    return [p for p in data if p.get('gen', p.get('generation')) == int(gen)]

def search_by_color(data, color):
    return [p for p in data if p.get('color', '').lower() == color.lower()]

def search_by_habitat(data, habitat):
    h = habitat.lower()
    return [p for p in data if h in p.get('habitat', '').lower()]

def search_by_species(data, species):
    s = species.lower()
    return [p for p in data if s in p.get('species', '').lower()]

def search_by_ability(data, extra_data, ability_query):
    """Find all Pokemon that have a given ability (regular or hidden)."""
    q = ability_query.lower()
    results = []
    for p in data:
        num = p.get('n', p.get('number'))
        extra = get_extra(extra_data, num)
        if extra:
            abilities_dict = extra.get('abilities', {})
            abilities = [
                abilities_dict.get('ability_1', ''),
                abilities_dict.get('ability_2', ''),
                abilities_dict.get('hidden_ability', '')
            ]
            if any(q in a.lower() for a in abilities if a):
                results.append(p)
    return results

def filter_legendary(data, extra_data, mythical=False, pseudo=False):
    """Filter for legendary, mythical, or pseudo-legendary Pokemon."""
    results = []
    for p in data:
        num = p.get('n', p.get('number'))
        extra = get_extra(extra_data, num)
        if extra:
            if pseudo and extra.get('is_pseudo_legendary'):
                results.append(p)
            elif mythical and extra.get('is_mythical'):
                results.append(p)
            elif not mythical and not pseudo and extra.get('is_legendary'):
                results.append(p)
    return results

def filter_by_bst(data, extra_data, min_bst=None, max_bst=None):
    """Filter Pokemon by Base Stat Total range."""
    results = []
    for p in data:
        num = p.get('n', p.get('number'))
        extra = get_extra(extra_data, num)
        if extra and extra.get('stats'):
            bst = extra['stats'].get('total', 0)
            if min_bst is not None and bst < min_bst:
                continue
            if max_bst is not None and bst > max_bst:
                continue
            results.append(p)
    return results

def type_chart_lookup(type_chart, type_name):
    name = type_name.strip().capitalize()
    if name not in type_chart:
        print(f"Type '{name}' not found. Valid types: {', '.join(sorted(type_chart.keys()))}")
        return
    info = type_chart[name]
    print(f"\n=== {name} Type Effectiveness ===")
    print(f"Weak to:    {', '.join(info['weaknesses']) or 'none'}")
    print(f"Resists:    {', '.join(info['resistances']) or 'none'}")
    print(f"Immune to:  {', '.join(info['immunities']) or 'none'}")

def dual_type_lookup(type_chart, type1, type2):
    """Calculate combined weaknesses/resistances for a dual-type Pokemon."""
    t1 = type1.strip().capitalize()
    t2 = type2.strip().capitalize()
    if t1 not in type_chart or t2 not in type_chart:
        print("Invalid type(s).")
        return

    all_types = list(type_chart.keys())
    effectiveness = {}

    for atk_type in all_types:
        mult = 1.0
        for def_type in [t1, t2]:
            info = type_chart[def_type]
            if atk_type in info['immunities']:
                mult *= 0
            elif atk_type in info['weaknesses']:
                mult *= 2
            elif atk_type in info['resistances']:
                mult *= 0.5
        effectiveness[atk_type] = mult

    print(f"\n=== {t1}/{t2} Dual Type Effectiveness ===")
    x4 = [t for t, m in effectiveness.items() if m == 4]
    x2 = [t for t, m in effectiveness.items() if m == 2]
    x05 = [t for t, m in effectiveness.items() if m == 0.5]
    x025 = [t for t, m in effectiveness.items() if m == 0.25]
    x0 = [t for t, m in effectiveness.items() if m == 0]

    if x4: print(f"4x weak:    {', '.join(x4)}")
    if x2: print(f"2x weak:    {', '.join(x2)}")
    if x05: print(f"0.5x resists: {', '.join(x05)}")
    if x025: print(f"0.25x resists: {', '.join(x025)}")
    if x0: print(f"Immune to:  {', '.join(x0)}")

def search_moves(moves, type_filter=None, category_filter=None, name_query=None,
                 min_power=None, max_power=None):
    """Search moves with optional filters."""
    results = moves
    if type_filter:
        t = type_filter.strip().capitalize()
        results = [m for m in results if m['type'] == t]
    if category_filter:
        c = category_filter.strip().upper()
        # P=Physical, S=Special, ST=Status
        results = [m for m in results if m['category'] == c]
    if name_query:
        q = name_query.lower()
        results = [m for m in results if q in m['name'].lower()]
    if min_power is not None:
        results = [m for m in results if m['power'] is not None and m['power'] >= min_power]
    if max_power is not None:
        results = [m for m in results if m['power'] is not None and m['power'] <= max_power]
    return results

def print_pokemon(p, verbose=False, extra=None):
    num = p.get('n', p.get('number'))
    forms_str = f" [{', '.join(p['forms'])}]" if p.get('forms') else ""
    print(f"\n#{num:04d} {p['name']}{forms_str}")
    print(f"  Type:     {p['type']}")
    print(f"  Gen:      {p.get('gen', p.get('generation'))}")
    print(f"  Species:  {p.get('species', '')}")
    print(f"  Habitat:  {p.get('habitat', '')}")
    print(f"  Color:    {p.get('color', '')}")
    print(f"  Height:   {p.get('height', p.get('height_m', ''))}m")
    print(f"  Weight:   {p.get('weight', p.get('weight_kg', ''))}kg")
    print(f"  Gender:   {p.get('gender', p.get('gender_ratio', ''))}")
    if p.get('desc'):
        print(f"  Desc:     {p['desc']}")
    if extra:
        stats = extra.get('stats', {})
        if stats:
            bst = stats.get('total', 0)
            print(f"  Base Stats: HP={stats.get('hp')} Atk={stats.get('attack')} Def={stats.get('defense')} "
                  f"SpA={stats.get('special_attack')} SpD={stats.get('special_defense')} Spe={stats.get('speed')} (BST={bst})")
        abilities_dict = extra.get('abilities', {})
        a1 = abilities_dict.get('ability_1', '')
        a2 = abilities_dict.get('ability_2', '')
        ha = abilities_dict.get('hidden_ability', '')
        abilities_str = ' / '.join(a for a in [a1, a2] if a)
        if ha:
            abilities_str += f" (H: {ha})"
        if abilities_str:
            print(f"  Abilities:  {abilities_str}")
        egg = extra.get('egg_groups', [])
        if egg:
            print(f"  Egg Groups: {', '.join(egg)}")
        catch = extra.get('catch_rate')
        if catch is not None:
            print(f"  Catch Rate: {catch}")
        if extra.get('is_legendary'):
            print(f"  [LEGENDARY]")
        elif extra.get('is_mythical'):
            print(f"  [MYTHICAL]")
        elif extra.get('is_pseudo_legendary'):
            print(f"  [PSEUDO-LEGENDARY]")
    if verbose and p.get('dex_entries'):
        print("  Pokedex Entries:")
        for game, entry in p.get('dex_entries', {}).items():
            print(f"    {game}: {entry}")

def print_move(m):
    power_str = str(m['power']) if m['power'] is not None else '—'
    acc_str = str(m['accuracy']) if m['accuracy'] is not None else '—'
    cat_full = {'P': 'Physical', 'S': 'Special', 'ST': 'Status'}.get(m['category'], m['category'])
    print(f"  {m['name']:<20} {m['type']:<10} {cat_full:<10} Pwr:{power_str:<5} Acc:{acc_str:<5} PP:{m['pp']}")
    if m.get('effect'):
        print(f"    {m['effect']}")

def print_summary(data):
    from collections import Counter
    gens = Counter(p.get('gen', p.get('generation')) for p in data)
    types = Counter()
    for p in data:
        for t in p['type'].split('/'):
            types[t.strip()] += 1

    print(f"\n=== Pokedex Summary ===")
    print(f"Total Pokemon: {len(data)}")
    print("\nBy Generation:")
    for g in sorted(gens.keys()):
        print(f"  Gen {g}: {gens[g]}")
    print("\nMost Common Types:")
    for t, c in types.most_common(10):
        print(f"  {t}: {c}")

def main():
    parser = argparse.ArgumentParser(description='Search the Pokemon Pokedex')
    # Pokemon filters
    parser.add_argument('--name', help='Search by name (partial match)')
    parser.add_argument('--number', type=int, help='Search by Pokedex number')
    parser.add_argument('--type', help='Filter by type (e.g. "fire" or "fire/flying")')
    parser.add_argument('--gen', type=int, help='Filter by generation (1-9)')
    parser.add_argument('--color', help='Filter by color')
    parser.add_argument('--habitat', help='Filter by habitat')
    parser.add_argument('--species', help='Filter by species keyword')
    # Stats/abilities
    parser.add_argument('--with-stats', action='store_true', help='Show base stats and abilities')
    parser.add_argument('--ability', help='Find Pokemon with this ability (regular or hidden)')
    parser.add_argument('--legendary', action='store_true', help='Show legendary Pokemon')
    parser.add_argument('--mythical', action='store_true', help='Show mythical Pokemon')
    parser.add_argument('--pseudo', action='store_true', help='Show pseudo-legendary Pokemon')
    parser.add_argument('--bst-min', type=int, help='Minimum Base Stat Total')
    parser.add_argument('--bst-max', type=int, help='Maximum Base Stat Total')
    # Type chart
    parser.add_argument('--type-chart', metavar='TYPE', help='Show type chart for a type')
    parser.add_argument('--dual-type', nargs=2, metavar=('TYPE1', 'TYPE2'), help='Dual-type effectiveness calculator')
    # Moves
    parser.add_argument('--moves', action='store_true', help='Search moves (use with --type, --category, --power-min)')
    parser.add_argument('--move-name', help='Look up a specific move by name')
    parser.add_argument('--move-type', help='Filter moves by type')
    parser.add_argument('--category', help='Filter moves by category: physical, special, or status')
    parser.add_argument('--power-min', type=int, help='Minimum move power')
    parser.add_argument('--power-max', type=int, help='Maximum move power')
    # Output
    parser.add_argument('--stats', action='store_true', help='Show summary statistics')
    parser.add_argument('--export', action='store_true', help='Export results as JSON')
    parser.add_argument('--verbose', '-v', action='store_true', help='Show all dex entries')
    parser.add_argument('--limit', type=int, default=50, help='Max results to show (default 50)')

    args = parser.parse_args()

    # Type chart operations don't need Pokemon data
    if args.type_chart:
        type_chart = load_type_chart()
        type_chart_lookup(type_chart, args.type_chart)
        return

    if args.dual_type:
        type_chart = load_type_chart()
        dual_type_lookup(type_chart, args.dual_type[0], args.dual_type[1])
        return

    # Move operations
    if args.moves or args.move_name or args.move_type:
        moves = load_moves()
        cat_map = {'physical': 'P', 'special': 'S', 'status': 'ST'}
        cat = cat_map.get((args.category or '').lower(), args.category)
        results = search_moves(
            moves,
            type_filter=args.move_type or args.type,
            category_filter=cat,
            name_query=args.move_name,
            min_power=args.power_min,
            max_power=args.power_max
        )
        print(f"\nFound {len(results)} move(s):")
        print(f"  {'Name':<20} {'Type':<10} {'Category':<10} {'Pwr':<6} {'Acc':<6} PP")
        print(f"  {'-'*70}")
        if args.export:
            print(json.dumps(results[:args.limit], ensure_ascii=False, indent=2))
        else:
            for m in results[:args.limit]:
                print_move(m)
            if len(results) > args.limit:
                print(f"\n... and {len(results) - args.limit} more.")
        return

    # Load data
    data = load_data(full=args.verbose)

    # Load extra data if needed
    extra_data = None
    needs_extra = (args.with_stats or args.ability or args.legendary or
                   args.mythical or args.pseudo or args.bst_min or args.bst_max)
    if needs_extra:
        extra_data = load_extra_data()

    if args.stats and not any([args.name, args.number, args.type, args.gen, args.color,
                               args.habitat, args.species, args.ability, args.legendary,
                               args.mythical, args.pseudo, args.bst_min, args.bst_max]):
        print_summary(data)
        return

    # Apply filters
    results = data

    if args.name:
        results = search_by_name(results, args.name)
    if args.number:
        results = search_by_number(results, args.number)
    if args.type:
        results = search_by_type(results, args.type)
    if args.gen:
        results = search_by_gen(results, args.gen)
    if args.color:
        results = search_by_color(results, args.color)
    if args.habitat:
        results = search_by_habitat(results, args.habitat)
    if args.species:
        results = search_by_species(results, args.species)
    if args.ability and extra_data:
        results = search_by_ability(results, extra_data, args.ability)
    if args.legendary and extra_data:
        results = filter_legendary(results, extra_data)
    if args.mythical and extra_data:
        results = filter_legendary(results, extra_data, mythical=True)
    if args.pseudo and extra_data:
        results = filter_legendary(results, extra_data, pseudo=True)
    if (args.bst_min or args.bst_max) and extra_data:
        results = filter_by_bst(results, extra_data, args.bst_min, args.bst_max)

    if not results:
        print("No Pokemon found matching those criteria.")
        return

    if args.export:
        print(json.dumps(results, ensure_ascii=False, indent=2))
        return

    print(f"\nFound {len(results)} Pokemon:")
    for p in results[:args.limit]:
        num = p.get('n', p.get('number'))
        extra = get_extra(extra_data, num) if extra_data else None
        print_pokemon(p, verbose=args.verbose, extra=extra if args.with_stats else None)

    if len(results) > args.limit:
        print(f"\n... and {len(results) - args.limit} more. Use --limit to see more.")

    if args.stats:
        print_summary(results)

if __name__ == '__main__':
    main()
