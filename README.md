# c-stdlib-rand-srand-footgun-lab

A tiny local correctness and safety lab about C `rand`, `srand`, `RAND_MAX`, hidden RNG state, seeding, modulo bias, `rand_r` availability, and embedded/newlib-style allocation caveats.

The lab uses a generated C harness compiled by a portable compiler (`zig cc`, `cc`, `clang`, or `gcc`) from a non-privileged Linux container. The point is **not** to reproduce newlib's malloc behavior, audit newlib, implement a cryptographic RNG, benchmark production PRNGs, compare every libc, run statistical batteries, or prove production RNG quality.

The point is to test the Hacker News debate in a tiny reproducible way: rand has hidden process-global state; srand resets that state; same seed repeats a sequence on the local libc but the sequence is implementation-defined; rand is not a CSPRNG; `rand() % n` can be biased; `RAND_MAX` limits matter; `rand_r` makes state explicit if available but is POSIX and not a quality guarantee; libraries that call rand can disturb caller expectations.

## Hacker News thread sentiments

This section summarizes the actual HN discussion at https://news.ycombinator.com/item?id=30942146 ("rand() may call malloc()"), accessed via the Hacker News API CLI before writing this README. See `hn_thread_evidence.md` for the audit trail.

The linked article (https://www.thingsquare.com/blog/articles/rand-may-call-malloc/) describes an embedded system with static-only allocation that hit a stack corruption crash traced to `rand()` calling `malloc()`. The cause: newlib configured with reentrancy support, where the reentrant wrapper around `rand()` allocates per-thread RNG state via `malloc()`. A toolchain update switched them to a reentrant newlib build.

HN commenters debated **what the real problem was**:

- **"stop using rand()"** – several commenters (raggi, chrsig) argued rand is bad regardless, and ditching it was the right pragmatic call, though the article's conclusion felt surface-level since the actual bug was newlib's reentrancy layer, not rand itself.
- **"stop using newlib"** – marcan_42 argued that in tight embedded systems with custom memory management you shouldn't have malloc at all, and newlib is too bloated; roll your own libc subset (e.g. PDClib pieces), use freestanding C. Others (klodolph, toast0, monocasa) pushed back: "roll your own" is a trap, it's easier to audit what newlib pulls in; you can pick pieces out of FreeBSD libc / PDClib / picolibc as needed.
- **"turn off reentrancy support"** – kevin_thibedeau, noobermin: newlib can be configured without reentrancy; that's the real fix if you want to keep newlib.
- **"remove malloc from the link / catch malloc callers in CI"** – zgs, MarkSweep, renox: if you're doing static-only allocation, why is malloc linked at all? Whitelist malloc callers in CI, catch this at link time. SAI_Peregrinus countered: sometimes you want dynamic allocation at startup only, then never again – in that design you can't just remove malloc.
- **"use a project-specific PRNG"** – broadly agreed as good practice. Several PRNG suggestions: PCG (SeanLuke criticized, jwmerrill defended), jart's lemur64 LCG, MWC, xoroshiro64s.

Other themes from the thread:

- **rand/srand hidden global state**: rand() uses process-global hidden state; srand() resets it. Libraries calling rand() internally break caller reproducibility – this came up repeatedly.
- **rand_r / caller-supplied state**: matthews2 pointed to `rand_r()` as the fix for thread-unsafe rand. The article actually showed `rand_r()` source code (labeled as `rand()` – a typo noted by unwind). `rand_r()` makes state explicit but is POSIX, not ISO C.
- **thread safety / reentrancy**: ajuc shared a university story: rand() wasn't thread-safe in their 3D demo, they added locks around rand() calls – which made multithreading useless. Should have used local PRNG state. Why newlib's reentrancy layer needed malloc: adrian_b explained – traditional C library functions use static variables; in multi-threaded programs those get clobbered. Newlib replaces static variables with dynamically-allocated per-thread variables. That's why rand() pulled in malloc.
- **embedded / static allocation**: embedded systems with kilobytes of RAM care deeply about unexpected malloc linkage. Heap fragmentation, stack depth measurement (`-Wstack-usage`), no dynamic allocation in RTOS – all discussed.
- **freestanding C / tiny libc subsets**: m1n1 (Asahi Linux) cited as example of freestanding C with embedded libc subset. PDClib, picolibc, picking FreeBSD libc pieces – all suggested.
- **Rust core/std**: Animats: "This is why Rust has both 'std' and 'core'. 'core' lacks allocation capability." Extended discussion about Rust embedded: binaries can be tiny (~145 bytes x86_64, ~500 bytes–10k ARM), turn off std, jemalloc, debug symbols, unwinding.
- **double-promotion footgun**: AdamH12113: "accidental promotions of floats to doubles" – C loves float promotion, easy to turn a one-cycle FPU op into a hundred-cycle softfloat call. Use `-Wdouble-promotion` / `-Werror=double-promotion`. Long thread about whether this is C's fault or the compiler's.
- **RAND_MAX / implementation-defined sequences / modulo bias / randomness quality**: treated as separate questions in the thread. rand quality debated (PCG criticism/defense, LCG constants discussion).
- **cryptographic security / deterministic seeds / time-based seeding / project-specific PRNGs**: commenters distinguished these use cases clearly – rand is wrong for crypto, fine-ish for toy games with caveats.
- **rand_r code correctness**: languageserver posted newlib's rand_r LCG code, questioned the `long s = (long)(*seed)` cast. adrian_b initially agreed it was wrong, then corrected: the constants 16807/127773 are carefully chosen to avoid overflow, the code is actually correct, just missing a comment warning not to change constants haphazardly.

### Why "rand is in the C standard library so it is fine" is not enough

The HN thread makes this clear from multiple angles: rand's sequence is implementation-defined (not portable across libcs/versions); rand has hidden global state that library calls disturb; rand is not thread-safe (without rand_r); rand is not cryptographic; `rand() % n` has modulo bias; `RAND_MAX` varies (minimum 32767 per ISO C, but actual values differ); newlib's reentrant wrapper pulled in malloc unexpectedly; embedded systems with static-only allocation need linker-level guarantees, not just API-level ones; and time-based seeding (`srand(time(NULL))`) is low-entropy and predictable.

## What this lab actually tests

55 deterministic synthetic cases covering:

- RAND_MAX recorded / minimum boundary marker
- unseeded rand sequence marker
- srand same seed repeats / different seeds change sequence (local observation)
- srand resets global state / rand consumes hidden global state
- library call disturbs caller sequence
- seed value vs RNG state distinction
- implementation-defined sequence / cross-libc not tested
- newlib malloc behavior NOT reproduced / malloc linkage NOT proven
- embedded static-allocation policy marker / linker audit NOT performed
- rand NOT cryptographic / time-based seed NOT run / low-entropy caveat
- modulo bias computed for n=2,10,100 / rejection sampling marker / bucket-count toy observation / low-bit caveat
- rand_r available/unavailable / explicit state / POSIX-not-ISO marker / quality NOT guaranteed
- thread race NOT run / locking NOT a quality fix / per-thread state NOT implemented
- project PRNG NOT implemented / deterministic game seed / fuzzing reproducibility
- library internal rand call / fork seed NOT tested / state serialization NOT portable
- strtol seed parsing (valid / trailing junk / range errno) / negative seed cast caveat / unsigned seed width caveat
- shuffle modulo / dice roll modulo markers
- security token / password reset token misuse NOT run
- CSPRNG alternative NOT used
- OpenBSD srand_deterministic NOT tested
- Rust core/std embedded comparison NOT tested
- double-promotion adjacent footgun NOT tested
- cleanup / no-global-reset-except-srand marker
- naive method expected-failure case

### Methods compared

- `preserve_original_case_baseline`
- `compiler_discovery_checker`
- `c_harness_compile_checker`
- `rand_srand_policy_observer`
- `hidden_state_marker`
- `modulo_bias_marker`
- `rand_r_policy_observer`
- `seed_parsing_policy_observer`
- `embedded_newlib_scope_marker`
- `crypto_security_scope_marker`
- `thread_reentrancy_scope_marker`
- `portability_scope_marker`
- `toy_project_prng_marker`
- `copy_size_timing_marker`
- `naive_rand_modulo_marker` – intentionally weak, assumes rand is crypto / unbiased / portable
- `external_rng_truth_not_tested_marker`

## Scope / what is NOT tested

This is a toy local lab, NOT a cryptography lab, NOT a security RNG, NOT a statistical test suite, NOT a newlib reproduction, NOT an embedded firmware build, NOT a linker audit, NOT a malloc interposition lab, NOT a sanitizer lab, NOT a C static analyzer, NOT a fuzzing target, NOT a libc conformance suite.

- No real secrets, real entropy, `/dev/random`, `/dev/urandom`, `getrandom`, `arc4random`, OpenSSL, libsodium
- No newlib source, glibc source, embedded firmware, cross-compilation
- No linker-map parsing, nm/objdump/readelf, malloc interposition, LD_PRELOAD
- No sanitizers, valgrind, fuzzing frameworks
- No external C libraries, PRNG libraries, crypto libraries
- No network calls during benchmark
- No statistical batteries (PractRand, TestU01, etc.)

Safe claims distinguish: what HN commenters discussed vs what the linked article claims vs what ISO C exposes vs what POSIX exposes vs what newlib-specific behavior claims vs what local libc actually does vs what this toy lab can prove.

## Running the lab

```
python3 -m py_compile generate_cases.py run_lab.py
python3 generate_cases.py
python3 run_lab.py
```

`run_lab.py` discovers a compiler in order: `zig cc`, `cc`, `clang`, `gcc`. No root installs, no package managers. Compiler path, version, compile command, and exit status are recorded in `RESULTS.md` and `VERIFY.md`.

If no usable compiler exists, the lab still runs – C-harness-dependent observations are marked `not_tested` with reason `compiler_not_available`. See `RESULTS.md` for environment status.

## Results

See [RESULTS.md](RESULTS.md) and `results_rows.csv` for per-case/per-method observations.

## Verify

See [VERIFY.md](VERIFY.md) for a fresh-clone verification transcript.

## Hacker News thread access

The Hacker News thread at https://news.ycombinator.com/item?id=30942146 was accessed via the Hacker News API CLI (`hackernews get-item --id 30942146`) before writing the sentiment summary in this README. The thread content was saved to `hn_thread_evidence.md` plus raw JSON at `hn_30942146.json` so the HN step is auditable. No direct quotes are included in the README above – sentiments are summarized in my own words.

## License

MIT / Public domain – this is a toy correctness lab.
