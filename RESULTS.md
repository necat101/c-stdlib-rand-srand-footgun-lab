# RESULTS — C rand/srand footgun lab

## Summary

- Cases: 55
- Methods: 16
- Total rows: 880
- Pass: 321
- Fail: 20
- Skip / not_tested / error: 539
- Expected-fail (naive): 20

## Compiler

- Compiler selected: not_found
- Compiler path: not_found
- Compiler version: not_found
- Compile command: ``
- Compile elapsed: 0.000s
- Compile OK: False
- Binary size: 0 bytes

## C Harness

- Harness: c_rand_srand_footgun_harness.c (4767 bytes)
- RAND_MAX observed: None
- rand_r available: False

## Scores by category

- compiler_availability_count: 1
- rand_srand_observation_count: 55
- randmax_observation_count: 32
- hidden_state_caveat_count: 55
- modulo_bias_caveat_count: 880
- rand_r_availability_count: 0
- seed_parsing_count: 48
- newlib_not_reproduced_count: 32
- malloc_linkage_not_proven_count: 32
- embedded_policy_marker_count: 85
- crypto_not_tested_count: 80
- thread_safety_not_tested_count: 48
- portability_not_tested_count: 96

## Artifacts

- per-case/per-method rows: results_rows.csv
- cases: cases.json (19185 bytes)
- harness: c_rand_srand_footgun_harness.c (4767 bytes)

## Environment

- Python: 3.12.3
- Platform: Linux-6.17.0-1009-aws-x86_64-with-glibc2.39
- Subprocess count: 1
- tracemalloc peak: 768640 bytes

## Scope / Honest conclusions

- HN-thread-access status: accessed via Hacker News API CLI – see hn_thread_evidence.md
- Network/API/package-manager status: no network calls during benchmark; HN thread fetched once before lab build
- Undefined-behavior-not-run status: no UB intentionally run
- newlib-malloc-not-reproduced status: NOT reproduced – toy local libc only
- cryptographic-security-not-tested status: NOT tested – rand is NOT a CSPRNG
- thread-safety-not-tested status: NOT tested – no thread races run
- portability-not-tested status: NOT tested – local libc only, sequences are implementation-defined

rand() has hidden process-global state; srand() resets it; same seed repeats on local libc but sequence is implementation-defined and NOT portable across libcs. rand() % n can be biased. rand is NOT cryptographic. rand_r provides explicit caller state but is POSIX, not ISO C, and is NOT a quality guarantee. Libraries calling rand() can disturb caller expectations. newlib malloc/reentrancy behavior, linker audits, embedded firmware, CSPRNGs, statistical batteries, and thread races were NOT tested.

This is a toy correctness/scope lab, not a cryptography lab, not a libc conformance suite, not a newlib reproduction.

## Run

```
python3 -m py_compile generate_cases.py run_lab.py
python3 generate_cases.py
python3 run_lab.py
```
