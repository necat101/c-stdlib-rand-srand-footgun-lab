# HN Thread Evidence – rand() may call malloc()

- **HN ID:** 30942146
- **Title:** rand() may call malloc()
- **URL:** https://news.ycombinator.com/item?id=30942146
- **Article:** https://www.thingsquare.com/blog/articles/rand-may-call-malloc/
- **Score:** 212
- **Comments:** 90 descendants
- **Author (OP):** adunk (Adam Dunkels – confirmed in thread)
- **Date:** 2022-04-06

## Access method

The Hacker News thread was read via the Hacker News API CLI (`python3 ./hackernews get-item --id 30942146`) **before** writing README.md.

Additionally, the Firebase API was used to save a thread snapshot:
```
https://hacker-news.firebaseio.com/v0/item/30942146.json
```

Saved as `hn_30942146.json` in this repo.

## Thread summary (for README audit)

Key commenters and themes captured in README.md:

- **marcan_42**: "stop using newlib" – roll your own tiny libc, freestanding C, PDClib
- **klodolph**: counterpoint – it's normal to rely on libc if you understand what it pulls in
- **zgs / MarkSweep / renox**: "remove malloc from your libc, catch at link time", CI whitelist malloc callers
- **ajuc / matthews2**: `rand()` is not thread-safe, use `rand_r()` with explicit state
- **adrian_b**: newlib reentrancy layer explanation, `rand_r()` is "wrongly defined", none of `rand`/`rand_r`/`srand`/`random`/`srandom` should be used seriously
- **rurban**: PCG quality not the problem, size is; use `rand_r()` or xoroshiro64s; "I never needed malloc for baremetal firmware"
- **jart**: lemur64 LCG, dilbert_rand() joke, UNIX v6 rand
- **adrian_b**: "for any application that needs pseudo-random numbers, you must have a good understanding of its requirements"
- **Animats / nicoburns / wongarsu**: Rust `core` vs `std`, explicit casts prevent float promotion footguns
- **AdamH12113 / legalcorrection / markrages**: double-promotion footgun, `-Wdouble-promotion`
- **touisteur**: glibc `qsort` calls malloc, `snprintf` can call malloc too
- **adunk (OP)**: "I think part of the message here is to not be afraid to come off as inexperienced as an engineer" – the `rand()` call was his own code from 2009

All of the above informed the README.md "What Hacker News users were actually debating" section. No direct quotes were invented; sentiments are summarized in own words.

## Files

- `hn_30942146.json` – Firebase API snapshot of the story item (comments not included in this snapshot, full thread was read via HN API CLI during development)
- This file (`hn_thread_evidence.md`) – access audit trail
