# Results – c-stdlib-rand-srand-footgun-lab

## Summary

- Cases: 53
- Methods: 16
- Pass: 367
- Fail: 7
- Expected naive failures: 7
- Skip/Not-tested/Not-applicable: 444

## Correctness counters

- rand/srand observations: 18
- RAND_MAX observations: 2
- hidden-state caveats: 6
- modulo-bias caveats: 8
- rand_r availability checks: 6
- seed-parsing checks: 3
- newlib NOT reproduced: 2
- malloc linkage NOT proven: 1
- embedded-policy markers: 2
- crypto NOT tested: 7
- thread-safety NOT tested: 3
- portability NOT tested: 6

## Build

- Compiler: zig cc
- Compiler path: /tmp/zig-linux-x86_64-0.13.0/zig
- Compiler version: clang version 18.1.6 (https://github.com/ziglang/zig-bootstrap 98bc6bf4fc4009888d33941daf6b600d20a42a56)
- Compile command: `/tmp/zig-linux-x86_64-0.13.0/zig cc -std=c11 -Wall -Wextra -O2 c_rand_srand_footgun_harness.c -o c_rand_harness`
- Compile time: 0.254s
- Harness C size: 5051 bytes
- Binary size: 18144 bytes
- Python: 3.12.3
- Platform: Linux-6.17.0-1009-aws-x86_64-with-glibc2.39
- Total run time: 0.690s

## Scope

- HN-thread-access: yes – Hacker News API CLI used before README
- Network/API during benchmark: no
- Entropy sources (/dev/urandom etc): no
- newlib malloc NOT reproduced: yes
- Cryptographic security NOT tested: yes
- Thread-safety NOT tested: yes
- Portability NOT tested: yes
- UB not run: yes

Per-case results: results_rows.csv / results_rows.json
