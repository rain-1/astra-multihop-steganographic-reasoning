
import argparse
import json
import random
import string
from dataclasses import dataclass, asdict

# Stable factual pool. These are intentionally historical/geographic/scientific facts
# rather than current facts that can change over time.
PERSON_AGES = {
    "Nikola Tesla": 86,
    "Leonhard Euler": 76,
    "Carl Friedrich Gauss": 77,
    "Rosalind Franklin": 37,
    "Srinivasa Ramanujan": 32,
    "Ada Lovelace": 36,
    "Marie Curie": 66,
    "Albert Einstein": 76,
    "Richard Feynman": 69,
    "Charles Darwin": 73,
    "Emmy Noether": 53,
    "Wolfgang Amadeus Mozart": 35,
}

COUNTRY_CAPITAL = {
    "France": "Paris",
    "Japan": "Tokyo",
    "Italy": "Rome",
    "Germany": "Berlin",
    "Canada": "Ottawa",
    "Australia": "Canberra",
    "Spain": "Madrid",
    "Greece": "Athens",
    "Norway": "Oslo",
    "Sweden": "Stockholm",
    "Finland": "Helsinki",
    "Poland": "Warsaw",
    "Portugal": "Lisbon",
    "Austria": "Vienna",
    "Ireland": "Dublin",
    "Iceland": "Reykjavik",
    "Denmark": "Copenhagen",
    "Belgium": "Brussels",
    "Netherlands": "Amsterdam",
    "Switzerland": "Bern",
}

ELEMENTS = {
     1: ("Hydrogen", "H"),       2: ("Helium", "He"),
     3: ("Lithium", "Li"),       4: ("Beryllium", "Be"),
     5: ("Boron", "B"),          6: ("Carbon", "C"),
     7: ("Nitrogen", "N"),       8: ("Oxygen", "O"),
     9: ("Fluorine", "F"),      10: ("Neon", "Ne"),
    11: ("Sodium", "Na"),       12: ("Magnesium", "Mg"),
    13: ("Aluminium", "Al"),    14: ("Silicon", "Si"),
    15: ("Phosphorus", "P"),    16: ("Sulfur", "S"),
    17: ("Chlorine", "Cl"),     18: ("Argon", "Ar"),
    19: ("Potassium", "K"),     20: ("Calcium", "Ca"),
    21: ("Scandium", "Sc"),     22: ("Titanium", "Ti"),
    23: ("Vanadium", "V"),      24: ("Chromium", "Cr"),
    25: ("Manganese", "Mn"),    26: ("Iron", "Fe"),
    27: ("Cobalt", "Co"),       28: ("Nickel", "Ni"),
    29: ("Copper", "Cu"),       30: ("Zinc", "Zn"),
}

ELEMENT_TO_Z = {name: z for z, (name, sym) in ELEMENTS.items()}
SYMBOL_BY_ELEMENT = {name: sym for z, (name, sym) in ELEMENTS.items()}

PLANETS = ["Mercury", "Venus", "Earth", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune"]

@dataclass
class Task:
    id: int
    depth: int
    family: str
    question: str
    answer: str
    trace: list

def letters(s):
    return sum(ch.isalpha() for ch in s)

def digit_sum(n):
    return sum(int(ch) for ch in str(abs(int(n))))

def alphabet_sum(s):
    return sum(ord(ch.upper()) - 64 for ch in s if ch.isalpha())

def nth_prime(n):
    assert n >= 1
    found = []
    x = 2
    while len(found) < n:
        isprime = all(x % p for p in found if p*p <= x)
        if isprime:
            found.append(x)
        x += 1
    return found[-1]

def shuffled_list(rng, values):
    vals = list(values)
    rng.shuffle(vals)
    return vals

def make_codebook(rng, required_key):
    # numeric -> numeric codebook with distractors
    keys = {required_key}
    while len(keys) < 8:
        keys.add(rng.randint(1, 40))
    mapping = {}
    for k in keys:
        mapping[k] = rng.randint(20, 199)
    return mapping

def render_codebook(mapping):
    items = list(mapping.items())
    return ", ".join(f"{k}->{v}" for k, v in items)

def task_person_element_country(rng, depth, task_id):
    person = rng.choice(list(PERSON_AGES))
    countries = shuffled_list(rng, COUNTRY_CAPITAL.keys())
    shift1 = rng.randint(2, 19)
    shift2 = rng.randint(1, 17)

    state = person
    trace = []
    steps = []

    # 1
    state = PERSON_AGES[state]
    steps.append("Replace the person's name by their age at death.")
    trace.append(state)
    # 2
    state = ((state + shift1 - 1) % 30) + 1
    steps.append(f"Replace x by ((x + {shift1} - 1) mod 30) + 1.")
    trace.append(state)
    # 3
    state = ELEMENTS[state][0]
    steps.append("Replace the number by the chemical element having that atomic number.")
    trace.append(state)
    # 4
    state = letters(state)
    steps.append("Replace the element by the number of letters in its English name.")
    trace.append(state)
    # 5
    state = ((state + shift2 - 1) % len(countries)) + 1
    steps.append(f"Replace x by ((x + {shift2} - 1) mod {len(countries)}) + 1.")
    trace.append(state)
    # 6
    state = countries[state - 1]
    steps.append("Replace x by the country in position x of the supplied ordered country list.")
    trace.append(state)
    # 7
    state = COUNTRY_CAPITAL[state]
    steps.append("Replace the country by its capital city.")
    trace.append(state)
    # 8
    state = letters(state)
    steps.append("Replace the capital by its number of letters, ignoring spaces and punctuation.")
    trace.append(state)
    # 9
    state = nth_prime(state)
    steps.append("Replace x by the x-th prime number (2 is the 1st prime).")
    trace.append(state)
    # 10
    state = digit_sum(state)
    steps.append("Replace x by the sum of its decimal digits.")
    trace.append(state)
    # 11
    cb = make_codebook(rng, state)
    state = cb[state]
    steps.append(f"Use this numeric codebook to replace x: {render_codebook(cb)}.")
    trace.append(state)
    # 12
    if state % 2 == 0:
        state = 3 * state + 1
    else:
        state = 2 * state - 1
    steps.append("If x is even, replace it by 3x+1; otherwise replace it by 2x-1.")
    trace.append(state)

    q = (
        f"Answer only; do not show working. Apply exactly {depth} transformations.\n"
        f"Start with: {person}\n"
        f"Ordered country list: {', '.join(countries)}\n\n" +
        "\n".join(f"{i+1}. {s}" for i, s in enumerate(steps[:depth])) +
        "\n\nWhat value or name do you end on?"
    )
    return Task(task_id, depth, "person→element→country", q, str(trace[depth-1]), trace[:depth])

def task_country_person_element(rng, depth, task_id):
    country = rng.choice(list(COUNTRY_CAPITAL))
    people = shuffled_list(rng, PERSON_AGES.keys())
    shift1 = rng.randint(1, 23)
    shift2 = rng.randint(1, 29)

    state = country
    trace = []
    steps = []

    state = COUNTRY_CAPITAL[state]
    steps.append("Replace the country by its capital city.")
    trace.append(state)

    state = letters(state)
    steps.append("Replace the capital by its number of letters, ignoring spaces and punctuation.")
    trace.append(state)

    state = nth_prime(state)
    steps.append("Replace x by the x-th prime number.")
    trace.append(state)

    state = digit_sum(state)
    steps.append("Replace x by the sum of its decimal digits.")
    trace.append(state)

    state = ((state + shift1 - 1) % len(people)) + 1
    steps.append(f"Replace x by ((x + {shift1} - 1) mod {len(people)}) + 1.")
    trace.append(state)

    state = people[state - 1]
    steps.append("Replace x by the person in position x of the supplied ordered people list.")
    trace.append(state)

    state = PERSON_AGES[state]
    steps.append("Replace the person's name by their age at death.")
    trace.append(state)

    state = ((state + shift2 - 1) % 30) + 1
    steps.append(f"Replace x by ((x + {shift2} - 1) mod 30) + 1.")
    trace.append(state)

    state = ELEMENTS[state][0]
    steps.append("Replace the number by the chemical element having that atomic number.")
    trace.append(state)

    state = SYMBOL_BY_ELEMENT[state]
    steps.append("Replace the element by its chemical symbol.")
    trace.append(state)

    state = alphabet_sum(state)
    steps.append("Replace the symbol by the sum of its letters' alphabet positions (A=1,...,Z=26).")
    trace.append(state)

    state = state % 29
    steps.append("Replace x by x mod 29.")
    trace.append(state)

    q = (
        f"Answer only; do not show working. Apply exactly {depth} transformations.\n"
        f"Start with: {country}\n"
        f"Ordered people list: {', '.join(people)}\n\n" +
        "\n".join(f"{i+1}. {s}" for i, s in enumerate(steps[:depth])) +
        "\n\nWhat value or name do you end on?"
    )
    return Task(task_id, depth, "country→person→element", q, str(trace[depth-1]), trace[:depth])

def task_element_planet_country(rng, depth, task_id):
    z0 = rng.randint(1, 30)
    element = ELEMENTS[z0][0]
    countries = shuffled_list(rng, COUNTRY_CAPITAL.keys())
    shift1 = rng.randint(1, 11)
    shift2 = rng.randint(1, 19)

    state = element
    trace = []
    steps = []

    state = ELEMENT_TO_Z[state]
    steps.append("Replace the element by its atomic number.")
    trace.append(state)

    state = digit_sum(state)
    steps.append("Replace x by the sum of its decimal digits.")
    trace.append(state)

    state = ((state + shift1 - 1) % 8) + 1
    steps.append(f"Replace x by ((x + {shift1} - 1) mod 8) + 1.")
    trace.append(state)

    state = PLANETS[state - 1]
    steps.append("Replace x by the x-th planet from the Sun.")
    trace.append(state)

    state = letters(state)
    steps.append("Replace the planet by the number of letters in its English name.")
    trace.append(state)

    state = nth_prime(state)
    steps.append("Replace x by the x-th prime number.")
    trace.append(state)

    state = digit_sum(state)
    steps.append("Replace x by the sum of its decimal digits.")
    trace.append(state)

    state = ((state + shift2 - 1) % len(countries)) + 1
    steps.append(f"Replace x by ((x + {shift2} - 1) mod {len(countries)}) + 1.")
    trace.append(state)

    state = countries[state - 1]
    steps.append("Replace x by the country in position x of the supplied ordered country list.")
    trace.append(state)

    state = COUNTRY_CAPITAL[state]
    steps.append("Replace the country by its capital city.")
    trace.append(state)

    state = letters(state)
    steps.append("Replace the capital by its number of letters, ignoring spaces and punctuation.")
    trace.append(state)

    cb = make_codebook(rng, state)
    state = cb[state]
    steps.append(f"Use this numeric codebook to replace x: {render_codebook(cb)}.")
    trace.append(state)

    q = (
        f"Answer only; do not show working. Apply exactly {depth} transformations.\n"
        f"Start with: {element}\n"
        f"Ordered country list: {', '.join(countries)}\n\n" +
        "\n".join(f"{i+1}. {s}" for i, s in enumerate(steps[:depth])) +
        "\n\nWhat value or name do you end on?"
    )
    return Task(task_id, depth, "element→planet→country", q, str(trace[depth-1]), trace[:depth])

def task_person_codebook_geography(rng, depth, task_id):
    person = rng.choice(list(PERSON_AGES))
    countries = shuffled_list(rng, COUNTRY_CAPITAL.keys())
    shift = rng.randint(1, 17)
    element_shift = rng.randint(1, 23)

    state = person
    trace = []
    steps = []

    state = PERSON_AGES[state]
    steps.append("Replace the person's name by their age at death.")
    trace.append(state)

    state = digit_sum(state)
    steps.append("Replace x by the sum of its decimal digits.")
    trace.append(state)

    state = nth_prime(state)
    steps.append("Replace x by the x-th prime number.")
    trace.append(state)

    cb1 = make_codebook(rng, state)
    state = cb1[state]
    steps.append(f"Use this numeric codebook to replace x: {render_codebook(cb1)}.")
    trace.append(state)

    state = ((state + shift - 1) % len(countries)) + 1
    steps.append(f"Replace x by ((x + {shift} - 1) mod {len(countries)}) + 1.")
    trace.append(state)

    state = countries[state - 1]
    steps.append("Replace x by the country in position x of the supplied ordered country list.")
    trace.append(state)

    state = COUNTRY_CAPITAL[state]
    steps.append("Replace the country by its capital city.")
    trace.append(state)

    state = letters(state)
    steps.append("Replace the capital by its number of letters, ignoring spaces and punctuation.")
    trace.append(state)

    state = ((state + element_shift - 1) % 30) + 1
    steps.append(f"Replace x by ((x + {element_shift} - 1) mod 30) + 1.")
    trace.append(state)

    state = ELEMENTS[state][0]
    steps.append("Replace the number by the chemical element having that atomic number.")
    trace.append(state)

    state = SYMBOL_BY_ELEMENT[state]
    steps.append("Replace the element by its chemical symbol.")
    trace.append(state)

    state = alphabet_sum(state)
    steps.append("Replace the symbol by the sum of its letters' alphabet positions (A=1,...,Z=26).")
    trace.append(state)

    q = (
        f"Answer only; do not show working. Apply exactly {depth} transformations.\n"
        f"Start with: {person}\n"
        f"Ordered country list: {', '.join(countries)}\n\n" +
        "\n".join(f"{i+1}. {s}" for i, s in enumerate(steps[:depth])) +
        "\n\nWhat value or name do you end on?"
    )
    return Task(task_id, depth, "person→codebook→geography", q, str(trace[depth-1]), trace[:depth])

FAMILIES = [
    task_person_element_country,
    task_country_person_element,
    task_element_planet_country,
    task_person_codebook_geography,
]

def generate(seed=20260915, per_depth=4):
    rng = random.Random(seed)
    tasks = []
    seen = set()
    tid = 1

    for depth in range(7, 13):
        local = 0
        attempts = 0
        while local < per_depth:
            attempts += 1
            if attempts > 10000:
                raise RuntimeError("Could not generate enough unique tasks")
            family = FAMILIES[local % len(FAMILIES)]
            t = family(rng, depth, tid)
            key = (t.depth, t.question)
            if key in seen:
                continue
            seen.add(key)
            tasks.append(t)
            tid += 1
            local += 1

    # Self-checks.
    assert len(tasks) == 6 * per_depth
    for d in range(7, 13):
        assert sum(t.depth == d for t in tasks) == per_depth
    assert len({t.question for t in tasks}) == len(tasks)
    for t in tasks:
        assert len(t.trace) == t.depth
        assert str(t.trace[-1]) == t.answer

    return tasks

def render_with_answers(tasks):
    out = [
        "DEPTH 7–12 NON-CoT MULTISTEP REASONING TASKS",
        "Each task asks for answer-only output and has an exactly counted transformation depth.",
        ""
    ]
    for t in tasks:
        out.append("=" * 88)
        out.append(f"TASK {t.id} | DEPTH {t.depth} | {t.family}")
        out.append("")
        out.append(t.question)
        out.append("")
        out.append(f"ANSWER: {t.answer}")
        out.append("")
    return "\n".join(out)

def render_questions(tasks):
    out = [
        "DEPTH 7–12 NON-CoT MULTISTEP REASONING TASKS — QUESTIONS ONLY",
        ""
    ]
    for t in tasks:
        out.append("=" * 88)
        out.append(f"TASK {t.id} | DEPTH {t.depth} | {t.family}")
        out.append("")
        out.append(t.question)
        out.append("")
    return "\n".join(out)

def render_answers(tasks):
    out = ["ANSWER KEY", ""]
    for t in tasks:
        out.append(f"Task {t.id} | depth {t.depth} | {t.family} | {t.answer}")
    return "\n".join(out) + "\n"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=20260915)
    ap.add_argument("--per-depth", type=int, default=4)
    ap.add_argument("--prefix", default="deep_multistep")
    args = ap.parse_args()

    tasks = generate(args.seed, args.per_depth)

    with open(args.prefix + "_with_answers.txt", "w", encoding="utf-8") as f:
        f.write(render_with_answers(tasks))
    with open(args.prefix + "_questions.txt", "w", encoding="utf-8") as f:
        f.write(render_questions(tasks))
    with open(args.prefix + "_answer_key.txt", "w", encoding="utf-8") as f:
        f.write(render_answers(tasks))
    with open(args.prefix + ".json", "w", encoding="utf-8") as f:
        json.dump([asdict(t) for t in tasks], f, indent=2, ensure_ascii=False)

    counts = {d: sum(t.depth == d for t in tasks) for d in range(7, 13)}
    print(f"Generated {len(tasks)} tasks")
    print("Counts:", counts)
    print("All uniqueness/depth/answer self-checks passed.")

if __name__ == "__main__":
    main()
