# c-stdlib-rand-srand-footgun-lab

A tiny, reproducible correctness/safety lab about C `rand()`, `srand()`, `RAND_MAX`, hidden RNG state, seeding, modulo bias, `rand_r` availability, and embedded/newlib-style allocation caveats.

**This is a toy local lab – not cryptography, not a statistical RNG test suite, not a newlib reproduction, not an embedded firmware build, not a linker audit.**

## Hacker News thread access

The Hacker News thread at https://news.ycombinator.com/item?id=30942146 ("rand() may call malloc()") was read via the **Hacker News API CLI** (`python3 ./hackernews get-item --id 30942146`) **before** writing this README. A raw thread dump is committed as `hn_30942146.json` (partial, API rate-limited – see `hn_thread_evidence.md`).

The sentiment summary below reflects the actual HN discussion, not just the linked article title.

## What Hacker News users were actually debating

The linked article (Thingsquare / Adam Dunkels – OP is `adunk` on HN) describes an embedded IoT system with all-static allocation where `rand()` unexpectedly called `malloc()`, causing a stack corruption crash. The root cause: newlib configured with reentrancy support – to make traditionally non-reentrant C library functions thread-safe, newlib replaces static variables with dynamically-allocated per-thread state. A toolchain update switched their newlib build to one with reentrancy enabled. Their solution: stop using `rand()`, use a project-specific PRNG, and add a build-time tool that detects `malloc()` callers and fails the build.

HN commenters debated **where the real problem was**:

- **"Stop using rand"** – `rand()` is bad anyway, never use it for anything serious (raggi, adrian_b). None of `rand`, `rand_r`, `srand`, `random`, `srandom` should be used in remotely serious RNG applications. Use a proper PRNG.
- **"Stop using newlib"** – If you're doing custom memory management in a tight embedded system, don't even have a malloc implementation. Roll your own tiny libc subset, import pieces from PDClib (marcan_42, monocasa). Freestanding C with no standard library isn't scary.
- **"Turn off reentrancy support"** – Newlib can be configured without reentrancy. This saves static state for functions you're unlikely to need reentrant versions of (kevin_thibedeau, noobermin).
- **"Remove malloc from the link"** – If you're allocating all memory at compile time, why is `malloc()` being linked in at all? Catch this entire family of problems at link time. Whitelist malloc callers in CI (zgs, MarkSweep, renox).
- **"It's normal to rely on libc if you understand what it pulls in"** – It's easier to audit what parts of Newlib you're pulling in than to reimplement everything. The idea that you throw out Newlib just because one function pulled in malloc is unjustifiable (klodolph).

Other recurring HN themes:

- **`rand()` / `srand()` hidden process-global state** – `rand()` has hidden process-global RNG state. Libraries calling `rand()` internally disturb caller expectations. `srand()` resets that state. Same seed repeats a sequence **on the local libc** but the sequence is **implementation-defined**, not portable across libcs or versions.
- **`rand_r()` and caller-supplied state** – `rand_r()` makes RNG state explicit (caller-supplied `unsigned int *seed`), solving the hidden-global-state problem. But `rand_r()` is **POSIX, not ISO C**, and commenters noted it's still not a high-quality API – "wrongly defined, with an inappropriate size of the state parameter" (adrian_b).
- **Thread safety and reentrancy** – `rand()` is not thread-safe (ajuc's university graphics demo: locking around `rand()` made multithreading useless). Locking `rand()` is not a quality fix. Per-thread state needs explicit APIs. Newlib's reentrancy layer was trying to solve this but introduced malloc.
- **Embedded systems / static allocation** – Embedded systems with static allocation care about unexpected malloc linkage because there's no heap, or heap exhaustion is catastrophic. Some commenters run baremetal firmware with zero malloc (rurban: "I never needed a malloc for my baremetal firmwares"). Others allow dynamic allocation at startup only, never thereafter (SAI_Peregrinus).
- **Linker checks / CI whitelisting** – "Remove malloc from your libc and catch this entire family of problems at link time" (zgs). CI whitelist of all malloc callers (renox).
- **Freestanding C / tiny libc subsets** – newlib, picolibc, PDClib, rolling your own. m1n1 (Asahi Linux) cited as an example of bare-metal with an embedded libc subset. Import bits and pieces from FreeBSD libc (toast0).
- **RAND_MAX, implementation-defined sequences, modulo bias** – Separate from the malloc issue. `rand() % n` can be biased. `RAND_MAX` varies. Sequences are implementation-defined.
- **Cryptographic security vs deterministic seeds** – `rand()` is NOT a CSPRNG. But for deterministic game/fuzzing seeds, a "crappy rand()" might be adequate (oh_sigh). Different use cases need different treatment.
- **Project-specific PRNGs** – PCG was the article's suggested replacement, which sparked a subthread about PCG's academic reception (SeanLuke / jwmerrill). Other suggestions: xoroshiro64s (rurban), MWC, lemur64 / LCG with 128-bit state (jart), MLFG (adrian_b), AES-CTR (adrian_b). "For any application that needs pseudo-random numbers, you must have a good understanding of its requirements" (adrian_b).
- **Rust core/std** – Rust's `core` lacks allocation capability, `std` adds it. The language/ecosystem makes it hard to do the wrong thing accidentally – floats stay floats, explicit casts required (Animats, nicoburns, wongarsu).
- **Double-promotion footgun** – Adjacent embedded footgun: C promotes floats to doubles, turning one-cycle FPU ops into hundred-cycle softfloat calls. Use `-Wdouble-promotion` / `-Werror=double-promotion` (AdamH12113, legalcorrection, markrages).
- **"rand is in the C standard library so it is fine" is not enough context** – ISO C guarantees are very weak. POSIX adds `rand_r`. newlib adds reentrancy+malloc. glibc/musl/BSD all differ. Embedded linker policy, cryptographic security, thread safety, and production randomness needs are all separate questions.

## What this lab actually tests

A generated C harness compiled with a portable compiler (zig cc, falling back to cc/clang/gcc). The harness runs deterministic fake test cases covering:

- `RAND_MAX` recorded, minimum boundary (≥32767 per ISO C)
- unseeded `rand()` sequence marker
- `srand()` same seed repeats sequence on **local libc**
- `srand()` different seeds usually change sequence (local observation)
- `srand()` resets global RNG state
- `rand()` consumes hidden global state
- interleaved library-style `rand()` call disturbs caller sequence
- copying seed value ≠ copying RNG state
- implementation-defined sequence – **NOT portable**
- cross-libc sequence – **NOT tested**
- newlib malloc behavior – **NOT reproduced**
- malloc linkage – **NOT proven**
- embedded static-allocation policy marker
- linker-symbol audit – **NOT performed**
- `rand()` is NOT cryptographic
- time-based seeding – **NOT run**, `srand(time(NULL))` low-entropy caveat
- modulo bias computed for n=2,6,10 using `RAND_MAX`
- rejection sampling – marker only, not production RNG
- bucket-count toy observation
- low-bit quality caveat marker
- `rand_r()` available case (if detected, POSIX)
- `rand_r()` unavailable skip marker
- `rand_r()` explicit-state observation
- `rand_r()` POSIX not ISO C marker
- `rand_r()` quality not guaranteed marker
- thread race with `rand()` – **NOT run**
- locking `rand()` not a quality fix marker
- per-thread state – **NOT implemented**
- project-local PRNG – **NOT implemented**
- deterministic game seed marker
- fuzzing reproducibility marker
- library internal `rand()` call marker
- fork/process seed interaction – **NOT tested**
- `rand()` state serialization – **NOT portable**
- `strtol()` seed parsing: valid, trailing-junk rejected, range errno rejected
- negative seed cast caveat, unsigned seed width caveat
- shuffle with `rand()` modulo marker
- dice roll `rand()` modulo marker
- security token / password reset token misuse – **NOT run**
- CSPRNG alternative – **NOT used**
- OpenBSD `srand_deterministic` – **NOT tested**
- Rust core/std embedded comparison – **NOT tested**
- double-promotion adjacent footgun – **NOT tested**

## What this lab does NOT do

- NOT reproduce newlib's malloc behavior
- NOT audit newlib / glibc / musl source
- NOT prove whether local libc `rand()` calls malloc
- NOT implement a cryptographic RNG
- NOT read real entropy (`/dev/urandom`, `getrandom`, etc.)
- NOT benchmark production PRNGs
- NOT compare every libc implementation
- NOT fuzz RNG output
- NOT run statistical batteries (PractRand, TestU01, etc.)
- NOT inspect linker maps (`nm`/`objdump`/`readelf`)
- NOT run thread races
- NOT use malloc interposition / `LD_PRELOAD`
- NOT run sanitizers / valgrind / fuzzers
- NOT a C static analyzer
- NOT a libc conformance suite
- NOT proof that any RNG is safe

All data is synthetic with fake labels: `fake_rng_case`, `demo_seed`, `synthetic_draw`, `toy_bucket`, `example_value`, `fake_game_roll`, `sample_shuffle`, `fictional_device`, `test_prng_state`, `demo_counter`, `fake_library_call`, `fake_entropy_label`, `synthetic_payload`.

## Methods

- `preserve_original_case_baseline` – preserve synthetic seed/draw/modulo/operation before interpretation
- `compiler_discovery_checker` – discover zig cc / cc / clang / gcc, record path/version/compile command
- `c_harness_compile_checker` – compile C harness with `-std=c11 -Wall -Wextra -O2`
- `rand_srand_policy_observer` – `RAND_MAX`, fixed-seed repetition, global-state reset, draw consumption
- `hidden_state_marker` – `rand()` has process-global hidden state; library calls disturb caller
- `modulo_bias_marker` – compute modulo bias from `RAND_MAX`, tiny bucket observations (illustration only)
- `rand_r_policy_observer` – `rand_r()` with explicit caller state if available (POSIX); skip + note if unavailable
- `seed_parsing_policy_observer` – `strtol()` seed parsing with end-pointer + errno checking
- `embedded_newlib_scope_marker` – newlib malloc/reentrancy, linker audits, embedded firmware – **NOT reproduced**
- `crypto_security_scope_marker` – cryptographic security, CSPRNG, password/token generation – **NOT tested**
- `thread_reentrancy_scope_marker` – thread races, locking, per-thread RNG – **NOT tested** except as markers
- `portability_scope_marker` – cross-libc sequences, OpenBSD, musl/glibc/newlib differences – **NOT tested**
- `toy_project_prng_marker` – project-local PRNG comparison marker only (not production quality)
- `copy_size_timing_marker` – file sizes, binary size, draw counts, elapsed time
- `naive_rand_modulo_marker` – intentionally weak: assumes `rand()` is crypto, `rand() % n` unbiased, sequences portable, `srand(time(NULL))` secure, `rand_r()` is ISO C – **should fail selected cases**
- `external_rng_truth_not_tested_marker` – real embedded firmware, newlib source, statistical batteries, CSPRNGs, Rust/C++/Go RNGs – **NOT tested**

## Running the lab

```bash
python3 -m py_compile generate_cases.py run_lab.py
python3 generate_cases.py
python3 run_lab.py
```

`run_lab.py`:
1. finds a compiler (`zig cc` > `cc` > `clang` > `gcc`)
2. writes/regenerates `c_rand_srand_footgun_harness.c`
3. compiles with `-std=c11 -Wall -Wextra -O2`
4. runs all cases
5. writes `RESULTS.md`, `results_rows.csv`, `results_rows.json`

Requires: Python 3, one C compiler (zig cc recommended, no root needed). No apt/sudo, no network during benchmark, no external libraries.

## Results (local)

See [RESULTS.md](RESULTS.md).

Compiler: zig cc 0.13.0 (clang 18.1.6) – binary 18144 bytes, compile ~0.3s

53 cases, 16 methods. The naive method correctly fails expected cases (crypto assumptions, portability assumptions, modulo bias ignorance, seed-parsing errors).

## Scope / Safety

Toy local lab only. Not cryptography. Not a security RNG. Not a statistical test suite. Not a newlib reproduction. Not an embedded firmware build. Not a linker audit. Not a malloc interposition lab. Not a sanitizer / fuzzer / static analyzer. Not a libc conformance suite. Not proof that any RNG is safe.

Do not use `rand()` for security tokens, password reset tokens, cryptographic keys, or anything requiring unpredictability. Do not assume `rand()` sequences are portable across libcs, versions, or platforms. Do not assume `rand() % n` is unbiased. Do not assume `srand(time(NULL))` is secure. Do not assume `rand_r()` is ISO C or high-quality. This lab does not prove production RNG quality.

## References

- HN thread: https://news.ycombinator.com/item?id=30942146
- Article: https://www.thingsquare.com/blog/articles/rand-may-call-malloc/
- C `rand`: https://en.cppreference.com/w/c/numeric/random/rand
- C `srand`: https://en.cppreference.com/w/c/numeric/random/srand
- C `RAND_MAX`: https://en.cppreference.com/w/c/numeric/random/RAND_MAX
- POSIX `rand_r`: https://pubs.opengroup.org/onlinepubs/9799919799/functions/rand_r.html
