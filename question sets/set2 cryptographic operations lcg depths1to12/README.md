# LCG scaling dataset

This deterministic dataset contains 36 new LCG PRNG tasks: three tasks at each
depth from 1 through 12. It retains the earlier recurrence
`x_(n+1) = (7*x_n + 3) mod 31` so results remain comparable with the pilot.

The seeded generator excludes starting states already used in the earlier
depth-4–12 datasets, rejects fixed points and any task whose state repeats
within its requested trace, and verifies every answer and trace.

The intended balanced evaluation has four conditions: unrestricted, unrelated,
punctuation, and unrelated + punctuation. Running all 36 questions under all
four conditions requires 144 samples. The three constrained conditions alone
would require 108 samples, but omitting the unrestricted baseline would make it
impossible to separate control effects from intrinsically difficult questions.
