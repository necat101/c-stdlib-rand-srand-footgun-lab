#!/usr/bin/env python3
"""Generate deterministic fake C rand/srand test cases."""
import json

cases = []

def add(cid, category, name, **kw):
    case = {"case_id": cid, "category": category, "fake_record_name": name}
    case.update(kw)
    cases.append(case)

# 1-5: RAND_MAX
add("c01_randmax_recorded", "randmax_recorded", "fake_rng_case_randmax",
    seed_value=None, draw_count=0,
    context_label="rand_policy",
    expected_outcome="success",
    expected_randmax_observation="recorded",
    reason=None, naive_should_fail=False)

add("c02_randmax_minimum", "randmax_minimum_marker", "demo_seed",
    seed_value=None, draw_count=0,
    context_label="rand_policy",
    expected_outcome="success",
    expected_randmax_observation="minimum_32767",
    reason="RAND_MAX >= 32767 per ISO C", naive_should_fail=False)

# 6-14: srand/sequence
add("c03_unseeded_sequence", "unseeded_sequence", "synthetic_draw",
    seed_value=None, draw_count=1,
    context_label="hidden_state_caveat",
    expected_outcome="success",
    expected_sequence_observation="local_only",
    reason=None, naive_should_fail=False)

add("c04_same_seed_repeats", "same_seed_repeats", "demo_seed",
    seed_value=12345, draw_count=5,
    context_label="rand_policy",
    expected_outcome="success",
    expected_sequence_observation="repeat_local",
    expected_reset_observation="reset",
    reason="same seed repeats on local libc", naive_should_fail=False)

add("c05_different_seed_changes", "different_seed_local_observation", "fake_rng_case",
    seed_value=54321, draw_count=5,
    context_label="rand_policy",
    expected_outcome="success",
    expected_sequence_observation="usually_changes",
    reason=None, naive_should_fail=False)

add("c06_srand_resets_global", "srand_resets_global_state", "test_prng_state",
    seed_value=42, draw_count=3,
    context_label="hidden_state_caveat",
    expected_outcome="success",
    expected_reset_observation="reset",
    reason=None, naive_should_fail=False)

add("c07_rand_consumes_state", "rand_consumes_global_state", "demo_counter",
    seed_value=7, draw_count=10,
    context_label="hidden_state_caveat",
    expected_outcome="success",
    expected_sequence_observation="consumes",
    reason=None, naive_should_fail=False)

add("c08_library_disturbs", "library_call_disturbs_sequence", "fake_library_call",
    seed_value=99, draw_count=5,
    context_label="hidden_state_caveat",
    expected_outcome="success",
    expected_sequence_observation="disturbed",
    reason="library rand() calls disturb caller", naive_should_fail=False)

add("c09_seed_not_state", "seed_not_state_marker", "test_prng_state",
    seed_value=None, draw_count=0,
    context_label="hidden_state_caveat",
    expected_outcome="not_applicable",
    expected_sequence_observation="not_portable",
    reason="copying seed != copying RNG state", naive_should_fail=True)

# 15-20: portability / newlib
add("c10_impl_defined_sequence", "implementation_defined_sequence", "synthetic_payload",
    seed_value=1, draw_count=3,
    context_label="portability_not_tested",
    expected_outcome="success",
    expected_sequence_observation="implementation_defined",
    portability_truth_not_tested=True,
    reason=None, naive_should_fail=False)

add("c11_cross_libc_not_tested", "cross_libc_not_tested", "fake_entropy_label",
    seed_value=1, draw_count=0,
    context_label="portability_not_tested",
    expected_outcome="not_tested",
    portability_truth_not_tested=True,
    reason="cross-libc sequence not tested", naive_should_fail=True)

add("c12_newlib_malloc_not_reproduced", "newlib_malloc_not_reproduced", "fictional_device",
    seed_value=None, draw_count=0,
    context_label="newlib_not_reproduced",
    expected_outcome="not_tested",
    newlib_truth_not_tested=True,
    reason="newlib malloc/reentrancy not reproduced", naive_should_fail=False)

add("c13_malloc_linkage_not_proven", "malloc_linkage_not_proven", "fictional_device",
    seed_value=None, draw_count=0,
    context_label="newlib_not_reproduced",
    expected_outcome="not_tested",
    newlib_truth_not_tested=True,
    reason="malloc linkage not proven", naive_should_fail=False)

add("c14_embedded_static_alloc", "embedded_static_allocation_marker", "fictional_device",
    seed_value=None, draw_count=0,
    context_label="embedded_policy_marker",
    expected_outcome="not_applicable",
    reason="embedded static-allocation policy marker", naive_should_fail=False)

add("c15_linker_audit_not_performed", "linker_audit_not_performed", "fictional_device",
    seed_value=None, draw_count=0,
    context_label="embedded_policy_marker",
    expected_outcome="not_tested",
    reason="linker-symbol audit not performed", naive_should_fail=False)

# 16-22: crypto / security
add("c16_rand_not_crypto", "rand_not_crypto", "fake_rng_case",
    seed_value=None, draw_count=0,
    context_label="crypto_not_tested",
    expected_outcome="success",
    security_truth_not_tested=True,
    reason="rand is not a CSPRNG", naive_should_fail=True)

add("c17_time_seed_not_run", "time_seed_not_run", "demo_seed",
    seed_value=None, draw_count=0,
    context_label="crypto_not_tested",
    expected_outcome="not_tested",
    security_truth_not_tested=True,
    reason="time-based seeding not run", naive_should_fail=False)

add("c18_srand_time_low_entropy", "srand_time_low_entropy", "demo_seed",
    seed_value=None, draw_count=0,
    context_label="crypto_not_tested",
    expected_outcome="not_applicable",
    security_truth_not_tested=True,
    reason="srand(time(NULL)) low-entropy caveat", naive_should_fail=True)

add("c19_security_token_misuse", "security_token_misuse_not_run", "example_value",
    seed_value=None, draw_count=0,
    context_label="security_not_tested",
    expected_outcome="not_tested",
    security_truth_not_tested=True,
    reason="security token misuse – not run", naive_should_fail=False)

add("c20_password_reset_misuse", "password_reset_token_misuse_not_run", "example_value",
    seed_value=None, draw_count=0,
    context_label="security_not_tested",
    expected_outcome="not_tested",
    security_truth_not_tested=True,
    reason="password reset token misuse – not run", naive_should_fail=False)

add("c21_csprng_not_used", "csprng_alternative_not_used", "fake_rng_case",
    seed_value=None, draw_count=0,
    context_label="crypto_not_tested",
    expected_outcome="not_tested",
    security_truth_not_tested=True,
    reason="CSPRNG alternative not used", naive_should_fail=False)

# 23-29: modulo bias
add("c22_modulo_bias_n2", "modulo_bias_computed", "toy_bucket",
    seed_value=None, draw_count=0, modulo_n=2,
    context_label="modulo_bias_caveat",
    expected_outcome="success",
    expected_modulo_bias_observation="computed",
    reason=None, naive_should_fail=False)

add("c23_modulo_bias_n6", "modulo_bias_computed", "fake_game_roll",
    seed_value=None, draw_count=0, modulo_n=6,
    context_label="modulo_bias_caveat",
    expected_outcome="success",
    expected_modulo_bias_observation="computed",
    reason="rand() % 6 bias check", naive_should_fail=False)

add("c24_modulo_bias_n10", "modulo_bias_computed", "toy_bucket",
    seed_value=None, draw_count=0, modulo_n=10,
    context_label="modulo_bias_caveat",
    expected_outcome="success",
    expected_modulo_bias_observation="computed",
    reason=None, naive_should_fail=False)

add("c25_rejection_sampling_marker", "rejection_sampling_marker", "toy_bucket",
    seed_value=None, draw_count=0,
    context_label="modulo_bias_caveat",
    expected_outcome="not_applicable",
    reason="rejection sampling not implemented as production RNG", naive_should_fail=False)

add("c26_bucket_count_toy", "bucket_count_toy_observation", "toy_bucket",
    seed_value=11, draw_count=1000, modulo_n=6,
    context_label="modulo_bias_caveat",
    expected_outcome="success",
    expected_modulo_bias_observation="observed",
    reason=None, naive_should_fail=False)

add("c27_low_bit_caveat", "low_bit_caveat", "fake_game_roll",
    seed_value=None, draw_count=0,
    context_label="modulo_bias_caveat",
    expected_outcome="not_applicable",
    reason="low-bit quality caveat", naive_should_fail=False)

add("c28_dice_roll_modulo", "dice_roll_modulo_marker", "fake_game_roll",
    seed_value=7, draw_count=10, modulo_n=6,
    context_label="modulo_bias_caveat",
    expected_outcome="success",
    expected_modulo_bias_observation="observed",
    reason=None, naive_should_fail=False)

# 30-37: rand_r
add("c29_rand_r_available", "rand_r_available", "test_prng_state",
    seed_value=123, draw_count=5,
    context_label="posix_extension_caveat",
    expected_outcome="success",
    expected_rand_r_observation="available_or_skip",
    reason=None, naive_should_fail=False)

add("c30_rand_r_unavailable", "rand_r_unavailable", "test_prng_state",
    seed_value=None, draw_count=0,
    context_label="posix_extension_caveat",
    expected_outcome="skip",
    expected_rand_r_observation="unavailable_ok",
    reason="rand_r is POSIX not ISO C", naive_should_fail=False)

add("c31_rand_r_explicit_state", "rand_r_explicit_state", "test_prng_state",
    seed_value=99, draw_count=5,
    context_label="posix_extension_caveat",
    expected_outcome="success",
    expected_rand_r_observation="explicit_state",
    reason=None, naive_should_fail=False)

add("c32_rand_r_posix_not_iso", "rand_r_posix_not_iso", "test_prng_state",
    seed_value=None, draw_count=0,
    context_label="posix_extension_caveat",
    expected_outcome="not_applicable",
    expected_rand_r_observation="posix_only",
    reason="rand_r POSIX not ISO C", naive_should_fail=True)

add("c33_rand_r_quality_not_guaranteed", "rand_r_quality_not_guaranteed", "test_prng_state",
    seed_value=None, draw_count=0,
    context_label="posix_extension_caveat",
    expected_outcome="not_applicable",
    reason="rand_r quality not guaranteed", naive_should_fail=False)

# 34-38: thread / reentrancy
add("c34_thread_race_not_run", "thread_race_not_run", "fake_rng_case",
    seed_value=None, draw_count=0,
    context_label="thread_safety_not_tested",
    expected_outcome="not_tested",
    thread_safety_truth_not_tested=True,
    reason="thread race with rand not run", naive_should_fail=False)

add("c35_locking_not_quality_fix", "locking_not_quality_fix", "fake_rng_case",
    seed_value=None, draw_count=0,
    context_label="thread_safety_not_tested",
    expected_outcome="not_applicable",
    thread_safety_truth_not_tested=True,
    reason="locking rand not a quality fix", naive_should_fail=False)

add("c36_per_thread_state_not_implemented", "per_thread_state_not_implemented", "test_prng_state",
    seed_value=None, draw_count=0,
    context_label="thread_safety_not_tested",
    expected_outcome="not_tested",
    thread_safety_truth_not_tested=True,
    reason="per-thread state not implemented", naive_should_fail=False)

# 39-44: project PRNG / game / fuzz
add("c37_project_prng_not_implemented", "project_prng_not_implemented", "fake_rng_case",
    seed_value=None, draw_count=0,
    context_label="portability_not_tested",
    expected_outcome="not_applicable",
    reason="project-local PRNG marker not implemented", naive_should_fail=False)

add("c38_deterministic_game_seed", "deterministic_game_seed_marker", "fake_game_roll",
    seed_value=777, draw_count=5,
    context_label="rand_policy",
    expected_outcome="success",
    expected_sequence_observation="repeat_local",
    reason=None, naive_should_fail=False)

add("c39_fuzzing_reproducibility", "fuzzing_reproducibility_marker", "synthetic_payload",
    seed_value=555, draw_count=5,
    context_label="rand_policy",
    expected_outcome="success",
    expected_sequence_observation="repeat_local",
    reason=None, naive_should_fail=False)

add("c40_library_internal_rand", "library_internal_rand_marker", "fake_library_call",
    seed_value=13, draw_count=3,
    context_label="hidden_state_caveat",
    expected_outcome="success",
    expected_sequence_observation="disturbed",
    reason="library internal rand call", naive_should_fail=False)

# 45-53: strtol seeding + misc
add("c41_strtol_seed_valid", "strtol_seed_valid", "demo_seed",
    seed_value=None, draw_count=0,
    context_label="rand_policy",
    expected_outcome="success",
    expected_strtol_observation="valid",
    expected_return_value_observation=12345,
    reason=None, naive_should_fail=False)

add("c42_strtol_trailing_junk", "strtol_seed_trailing_junk", "demo_seed",
    seed_value=None, draw_count=0,
    context_label="rand_policy",
    expected_outcome="error",
    expected_strtol_observation="trailing_junk",
    reason="strtol trailing-junk seed rejected", naive_should_fail=True)

add("c43_strtol_range_errno", "strtol_seed_range_errno", "demo_seed",
    seed_value=None, draw_count=0,
    context_label="rand_policy",
    expected_outcome="error",
    expected_strtol_observation="range_errno",
    expected_errno_observation="ERANGE",
    reason="strtol range errno seed rejected", naive_should_fail=True)

add("c44_negative_seed_cast", "negative_seed_cast_caveat", "demo_seed",
    seed_value=None, draw_count=0,
    context_label="rand_policy",
    expected_outcome="not_applicable",
    reason="negative seed cast caveat", naive_should_fail=False)

add("c45_unsigned_seed_width", "unsigned_seed_width_caveat", "demo_seed",
    seed_value=None, draw_count=0,
    context_label="rand_policy",
    expected_outcome="not_applicable",
    reason="unsigned seed width caveat", naive_should_fail=False)

add("c46_shuffle_modulo", "shuffle_modulo_marker", "sample_shuffle",
    seed_value=42, draw_count=10, modulo_n=10,
    context_label="modulo_bias_caveat",
    expected_outcome="success",
    expected_modulo_bias_observation="observed",
    reason=None, naive_should_fail=False)

add("c47_openbsd_srand_not_tested", "openbsd_srand_deterministic_not_tested", "fake_rng_case",
    seed_value=None, draw_count=0,
    context_label="portability_not_tested",
    expected_outcome="not_tested",
    portability_truth_not_tested=True,
    reason="OpenBSD srand_deterministic not tested", naive_should_fail=False)

add("c48_rust_core_not_tested", "rust_core_std_not_tested", "fake_rng_case",
    seed_value=None, draw_count=0,
    context_label="portability_not_tested",
    expected_outcome="not_tested",
    portability_truth_not_tested=True,
    reason="Rust core/std embedded comparison not tested", naive_should_fail=False)

add("c49_double_promotion_not_tested", "double_promotion_not_tested", "example_value",
    seed_value=None, draw_count=0,
    context_label="portability_not_tested",
    expected_outcome="not_tested",
    reason="double-promotion adjacent footgun not tested", naive_should_fail=False)

add("c50_fork_seed_not_tested", "fork_seed_not_tested", "fake_rng_case",
    seed_value=None, draw_count=0,
    context_label="portability_not_tested",
    expected_outcome="not_tested",
    portability_truth_not_tested=True,
    reason="fork/process seed interaction not tested", naive_should_fail=False)

add("c51_rand_state_serialization_not_portable", "rand_state_serialization_not_portable", "test_prng_state",
    seed_value=None, draw_count=0,
    context_label="portability_not_tested",
    expected_outcome="not_tested",
    portability_truth_not_tested=True,
    reason="serialization of rand state not portable", naive_should_fail=False)

add("c52_cleanup_marker", "cleanup_marker", "synthetic_payload",
    seed_value=None, draw_count=0,
    context_label="rand_policy",
    expected_outcome="success",
    reason="cleanup/no-global-reset-except-srand", naive_should_fail=False)

add("c53_safety_caveat", "safety_caveat", "fake_rng_case",
    seed_value=None, draw_count=0,
    context_label="crypto_not_tested",
    expected_outcome="not_applicable",
    security_truth_not_tested=True,
    reason="toy lab – not production RNG quality", naive_should_fail=False)

with open("cases.json", "w") as f:
    json.dump(cases, f, indent=2)

print(f"Generated {len(cases)} cases -> cases.json")
