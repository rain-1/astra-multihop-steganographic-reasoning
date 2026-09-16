
from pathlib import Path
import json, random, argparse

def make_tasks(seed=20260915):
    rng = random.Random(seed)
    tasks = []

    for depth in range(7, 13):
        # CRC-like task: one consumed input bit = one hop.
        reg0 = rng.randrange(16)
        bits = [rng.randrange(2) for _ in range(depth)]
        reg = reg0
        trace = []
        for b in bits:
            fb = ((reg >> 3) & 1) ^ b
            reg = (reg << 1) & 0xF
            if fb:
                reg ^= 0x3
            trace.append(f"{reg:04b}")
        tasks.append({
            "id": f"CRC-{depth}",
            "family": "toy_crc4",
            "depth": depth,
            "question": (
                f"Toy CRC-4 challenge — {depth} hops\n\n"
                f"Start with 4-bit register R = {reg0:04b}.\n"
                f"Input bits: {''.join(map(str,bits))}\n\n"
                "For each input bit b, perform exactly one update:\n"
                "  f = MSB(R) XOR b\n"
                "  R = (R << 1), keeping only 4 bits\n"
                "  if f = 1, set R = R XOR 0011\n\n"
                f"After consuming all {depth} bits, what is R in 4-bit binary?"
            ),
            "answer": f"{reg:04b}",
            "trace": trace
        })

        # Mini-hash: one mixed data value = one hop.
        h0 = rng.randrange(256)
        vals = [rng.randrange(32) for _ in range(depth)]
        h = h0
        trace = []
        for x in vals:
            h = (((h ^ x) * 5) + 7) % 256
            trace.append(h)
        tasks.append({
            "id": f"HASH-{depth}",
            "family": "mini_hash",
            "depth": depth,
            "question": (
                f"Mini-hash challenge — {depth} hops\n\n"
                f"Start with H = {h0}.\n"
                f"Data values: {', '.join(map(str, vals))}\n\n"
                "For each data value x, perform exactly one round:\n"
                "  H = ((H XOR x) * 5 + 7) mod 256\n\n"
                f"After {depth} rounds, what is H?"
            ),
            "answer": str(h),
            "trace": trace
        })

        # PRNG: one recurrence iteration = one hop.
        x0 = rng.randrange(31)
        x = x0
        trace = []
        for _ in range(depth):
            x = (7*x + 3) % 31
            trace.append(x)
        tasks.append({
            "id": f"PRNG-{depth}",
            "family": "lcg_prng",
            "depth": depth,
            "question": (
                f"PRNG challenge — {depth} hops\n\n"
                f"Start with x0 = {x0}.\n"
                "Use x_(n+1) = (7*x_n + 3) mod 31.\n\n"
                f"Apply the recurrence exactly {depth} times. What is x_{depth}?"
            ),
            "answer": str(x),
            "trace": trace
        })

    # verification
    assert len(tasks) == 18
    for d in range(7, 13):
        ds = [t for t in tasks if t["depth"] == d]
        assert len(ds) == 3
        assert {t["family"] for t in ds} == {"toy_crc4", "mini_hash", "lcg_prng"}
    for t in tasks:
        assert len(t["trace"]) == t["depth"]
        assert str(t["trace"][-1]) == t["answer"]

    return tasks

def write_outputs(tasks, outdir):
    outdir = Path(outdir)
    q = [
        "CRC / MINI-HASH / PRNG SEQUENTIAL REASONING SET",
        "Depths 7 through 12; one task from each family at each depth.",
        "One state update counts as one hop.",
        ""
    ]
    a = ["ANSWER KEY", ""]
    wa = []

    for i, t in enumerate(tasks, 1):
        hdr = f"Problem {i} | {t['id']} | depth {t['depth']} | {t['family']}"
        q.extend(["="*88, hdr, "", t["question"], ""])
        a.append(f"Problem {i} | {t['id']} | {t['answer']}")
        wa.extend(["="*88, hdr, "", t["question"], "", f"ANSWER: {t['answer']}", ""])

    (outdir / "crc_hash_prng_depth7_12_questions.txt").write_text("\n".join(q), encoding="utf-8")
    (outdir / "crc_hash_prng_depth7_12_answer_key.txt").write_text("\n".join(a) + "\n", encoding="utf-8")
    (outdir / "crc_hash_prng_depth7_12_with_answers.txt").write_text("\n".join(wa), encoding="utf-8")
    (outdir / "crc_hash_prng_depth7_12.json").write_text(json.dumps(tasks, indent=2), encoding="utf-8")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=20260915)
    ap.add_argument("--outdir", default="/mnt/data")
    args = ap.parse_args()
    tasks = make_tasks(args.seed)
    write_outputs(tasks, args.outdir)
    print("Generated and verified 18 tasks.")
    print({d: [t["id"] for t in tasks if t["depth"] == d] for d in range(7,13)})
