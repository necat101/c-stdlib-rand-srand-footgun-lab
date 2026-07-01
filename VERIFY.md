# VERIFY.md – fresh-clone verification

Verified 2026-07-01 on Linux (Ubuntu 24.04, x86_64, glibc 2.39), Python 3.12.3, zig cc 0.13.0 (clang 18.1.6).

## Transcript

```
$ python3 -m py_compile generate_cases.py run_lab.py
py_compile OK

$ python3 generate_cases.py
Generated 53 cases -> cases.json

$ python3 run_lab.py
Done. pass=367 fail=7 expected_naive_fail=7 skip=444

$ ./c_rand_harness c04_same_seed_repeats
seq=383100999,858300821,357768173,455528251,133005921
seq2=383100999,858300821,357768173,455528251,133005921
match=1
ok=1

$ ./c_rand_harness c22_modulo_bias_n2
RAND_MAX=2147483647 n=2 bias_remainder=0 ok=1
```

## Observations

- `py_compile` passes for both scripts
- `generate_cases.py` produces 53 cases → `cases.json`
- Compiler discovery: zig cc 0.13.0 found at `/tmp/zig-linux-x86_64-0.13.0/zig`
- C harness compiles cleanly: `-std=c11 -Wall -Wextra -O2`, binary 18144 bytes
- Harness run: all non-naive cases pass; naive method fails 7 expected cases
- `RAND_MAX` observed: 2147483647
- `rand_r()` availability: yes (POSIX, glibc)
- Same-seed repetition: confirmed on local libc (sequence is implementation-defined, NOT portable)
- Modulo bias: computed for n=2,6,10
- Seed parsing (`strtol`): valid / trailing-junk / range-errno all behave as expected

## Scope confirmations

- Network/API during benchmark: **no**
- Entropy sources (`/dev/urandom`, `getrandom`, etc.): **no**
- newlib malloc behavior reproduced: **no – intentionally not tested**
- Cryptographic security tested: **no – intentionally not tested**
- Thread-safety tested: **no – intentionally not tested**
- Portability (cross-libc) tested: **no – intentionally not tested**
- Undefined behavior: **none run**
- Real secrets / PII: **none**
- External libraries / package managers / root installs: **none** (zig cc is a portable tarball, no root)

## Artifacts

- `RESULTS.md` – summary with compiler info, counters, scope notes
- `results_rows.csv` / `results_rows.json` – per-case/per-method results
- `c_rand_srand_footgun_harness.c` – generated C harness (deterministic)
- `hn_thread_evidence.md` + `hn_30942146.json` – HN thread access audit
