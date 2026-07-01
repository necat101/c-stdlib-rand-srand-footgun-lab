# VERIFY — c-stdlib-rand-srand-footgun-lab

Fresh-clone verification transcript. Run from a clean clone of the repo.

```
$ python3 -m py_compile generate_cases.py run_lab.py
py_compile: OK

$ python3 generate_cases.py
Wrote 55 cases to cases.json

$ python3 run_lab.py
Loaded 55 cases
WARNING: no compiler found (tried zig cc, cc, clang, gcc) – C harness will be not_tested
Compiler: not_found @ not_found
  not_found
Compile: SKIPPED – no compiler available
RAND_MAX = not_tested (no compiler)
rand_r_available = not_tested (no compiler)

Done. pass=321 fail=20 skip=539 naive_expected_fail=20
results_rows.csv: 880 rows
```

## Environment

- OS: Linux (container, non-privileged, no root)
- Python: 3.12
- Compiler: **not_found** – searched `zig cc`, `cc`, `clang`, `gcc`, none available in PATH
- C harness status: **not_tested** – `c_rand_srand_footgun_harness.c` is present in the repo but was not compiled/validated in this environment due to missing compiler
- RAND_MAX observation: not_tested (no compiler)
- rand_r availability: not_tested (no compiler)

## Artifacts produced

- `cases.json` – 55 cases
- `results_rows.csv` – 880 rows (55 cases × 16 methods)
- `RESULTS.md` – summary with compiler_not_available note

## Scope notes

- No network calls during benchmark
- No entropy / secrets / CSPRNG / real RNG
- No newlib reproduction, no malloc interposition, no linker audit
- No thread races, no sanitizers, no fuzzing
- No external libraries, package managers, or root installs
- HN thread accessed via Hacker News API CLI before README was written – see `hn_thread_evidence.md` / `hn_30942146.json`
- Cryptographic security: NOT tested
- Thread safety: NOT tested
- Portability (cross-libc): NOT tested
- newlib malloc behavior: NOT reproduced

This is a toy correctness/scope lab. C harness observations are marked `not_tested` in this verification run due to missing compiler in the sandbox environment. The harness source (`c_rand_srand_footgun_harness.c`) is committed and deterministic – compile with any C11 compiler to validate locally:

```
cc -std=c11 -Wall -Wextra -O2 c_rand_srand_footgun_harness.c -o c_harness
./c_harness randmax
./c_harness draw 42 8
./c_harness same_seed_repeat 42 8
```
