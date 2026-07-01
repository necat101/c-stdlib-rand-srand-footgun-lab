#!/usr/bin/env python3
"""
generate_cases.py — C rand/srand footgun lab case generator

Deterministic synthetic cases only. No real entropy, no secrets.
"""
import json, os

cases = []

def add(cid, category, fake_name, **kw):
    case = {"case_id": cid, "category": category, "fake_record_name": fake_name}
    case.update(kw)
    cases.append(case)

# 1-55 cases covering the required topics
add("c01", "randmax", "fake_rng_case_randmax", context_label="rand_policy",
    randmax_recorded=True, expected_success="success",
    expected_observation="RAND_MAX_value_recorded",
    expected_reason="record RAND_MAX from limits.h / stdlib.h")

add("c02", "randmax", "fake_rng_case_randmax_min", context_label="rand_policy",
    randmax_minimum_marker=True, expected_success="success",
    expected_observation="RAND_MAX_gte_32767_per_iso_c",
    expected_reason="ISO C requires RAND_MAX >= 32767")

add("c03", "unseeded", "demo_seed_unseeded", context_label="srand_policy",
    unseeded_sequence=True, expected_success="success",
    expected_observation="unseeded_rand_behaves_like_srand_1",
    expected_reason="ISO C: rand() without prior srand() behaves as if srand(1) was called")

add("c04", "same_seed", "synthetic_draw_seed42_a", seed_value=42, draw_count=8,
    context_label="srand_policy", same_seed_repeats=True, expected_success="success",
    expected_observation="same_seed_repeats_locally", expected_reason="srand resets global state deterministically on local libc")

add("c05", "same_seed", "synthetic_draw_seed1234_a", seed_value=1234, draw_count=8,
    context_label="srand_policy", same_seed_repeats=True, expected_success="success",
    expected_observation="same_seed_repeats_locally")

add("c06", "different_seed", "demo_seed_diff_1", seed_value=1, draw_count=5,
    context_label="srand_policy", different_seed_local_observation=True, expected_success="success",
    expected_observation="different_seeds_usually_change_sequence_local",
    expected_reason="local observation only, not a portability guarantee")

add("c07", "different_seed", "demo_seed_diff_2", seed_value=999, draw_count=5,
    context_label="srand_policy", different_seed_local_observation=True, expected_success="success",
    expected_observation="different_seeds_usually_change_sequence_local")

add("c08", "srand_reset", "test_prng_state_reset", seed_value=555, draw_count=4,
    context_label="hidden_state_caveat", srand_resets_global_state=True, expected_success="success",
    expected_observation="srand_resets_global_rng_state")

add("c09", "rand_consumes", "demo_counter_draws", seed_value=7, draw_count=10,
    context_label="hidden_state_caveat", rand_consumes_global_state=True, expected_success="success",
    expected_observation="each_rand_call_consumes_global_state")

add("c10", "library_disturb", "fake_library_call_a", seed_value=100, draw_count=6,
    context_label="hidden_state_caveat", library_call_disturbs_sequence=True, expected_success="success",
    expected_observation="interleaved_library_rand_disturbs_caller_sequence",
    expected_reason="hidden process-global state: library calls to rand change caller's sequence")

add("c11", "seed_not_state", "test_prng_state_copy_marker", seed_value=42,
    context_label="hidden_state_caveat", seed_not_state_marker=True, expected_success="success",
    expected_observation="copying_seed_value_is_not_copying_rng_state")

add("c12", "implementation_defined", "example_value_impl_def", seed_value=42, draw_count=3,
    context_label="portability_not_tested", implementation_defined_sequence=True, expected_success="success",
    expected_observation="rand_sequence_is_implementation_defined",
    expected_reason="ISO C does not specify rand algorithm; sequences differ across libcs/versions")

add("c13", "cross_libc", "fake_rng_case_cross_libc", context_label="portability_not_tested",
    cross_libc_not_tested=True, expected_success="not_tested",
    expected_observation="cross_libc_sequence_not_tested",
    expected_reason="this lab tests local libc only")

add("c14", "newlib_malloc", "fictional_device_newlib", context_label="newlib_not_reproduced",
    newlib_malloc_not_reproduced=True, expected_success="not_tested",
    expected_observation="newlib_malloc_reentrancy_not_reproduced",
    expected_reason="HN article theme: newlib rand() pulled in malloc via reentrancy support – not reproduced in this toy lab")

add("c15", "malloc_linkage", "synthetic_payload_malloc_link", context_label="newlib_not_reproduced",
    malloc_linkage_not_proven=True, expected_success="not_tested",
    expected_observation="malloc_linkage_not_proven_locally")

add("c16", "embedded_static", "fictional_device_static_alloc", context_label="embedded_policy_marker",
    embedded_static_allocation_marker=True, expected_success="success",
    expected_observation="embedded_static_allocation_policy_marker",
    expected_reason="HN debate: embedded systems with static allocation care about unexpected malloc linkage")

add("c17", "linker_audit", "fake_entropy_label_linker", context_label="embedded_policy_marker",
    linker_audit_not_performed=True, expected_success="not_tested",
    expected_observation="linker_symbol_audit_not_performed")

add("c18", "crypto_marker", "fake_entropy_label_crypto", context_label="crypto_not_tested",
    rand_not_crypto=True, expected_success="success",
    expected_observation="rand_is_not_a_csprng",
    expected_reason="rand is not cryptographically secure – do not use for security tokens")

add("c19", "time_seed", "demo_seed_time_marker", context_label="srand_policy",
    time_seed_not_run=True, expected_success="not_tested",
    expected_observation="time_based_seed_not_run",
    expected_reason="time(NULL) seeding not executed – low entropy, predictable")

add("c20", "srand_time_low_entropy", "fake_game_roll_time_seed", context_label="crypto_not_tested",
    srand_time_low_entropy=True, expected_success="success",
    expected_observation="srand_time_null_low_entropy_caveat")

add("c21", "modulo_bias", "toy_bucket_mod_2", modulo_n=2, context_label="modulo_bias_caveat",
    modulo_bias_computed=True, expected_success="success",
    expected_observation="modulo_bias_computed_from_rand_max",
    expected_reason="rand() % n can be biased when RAND_MAX+1 not divisible by n")

add("c22", "modulo_bias", "toy_bucket_mod_10", modulo_n=10, context_label="modulo_bias_caveat",
    modulo_bias_computed=True, expected_success="success",
    expected_observation="modulo_bias_computed_from_rand_max")

add("c23", "modulo_bias", "toy_bucket_mod_100", modulo_n=100, context_label="modulo_bias_caveat",
    modulo_bias_computed=True, expected_success="success",
    expected_observation="modulo_bias_computed_from_rand_max")

add("c24", "rejection_sampling", "sample_shuffle_reject_marker", context_label="modulo_bias_caveat",
    rejection_sampling_marker=True, expected_success="not_tested",
    expected_observation="rejection_sampling_marker_not_implemented_as_production_rng")

add("c25", "bucket_count", "toy_bucket_counts", seed_value=999, draw_count=1000, modulo_n=10,
    context_label="modulo_bias_caveat", bucket_count_toy_observation=True, expected_success="success",
    expected_observation="bucket_count_toy_observation_local_only")

add("c26", "low_bit", "example_value_low_bits", context_label="modulo_bias_caveat",
    low_bit_caveat=True, expected_success="success",
    expected_observation="low_bit_quality_caveat_marker",
    expected_reason="historical rand implementations had poor low-bit quality")

add("c27", "rand_r_avail", "fake_rng_case_rand_r_check", context_label="posix_extension_caveat",
    rand_r_available=True, expected_success="success",
    expected_observation="rand_r_explicit_state_if_available",
    expected_reason="rand_r makes state explicit – POSIX, not ISO C")

add("c28", "rand_r_unavail", "fake_rng_case_rand_r_skip", context_label="posix_extension_caveat",
    rand_r_unavailable=True, expected_success="skip",
    expected_observation="rand_r_unavailable_skip",
    expected_reason="rand_r is POSIX, not ISO C – may be unavailable")

add("c29", "rand_r_explicit", "test_prng_state_rand_r", context_label="posix_extension_caveat",
    rand_r_explicit_state=True, expected_success="success",
    expected_observation="rand_r_explicit_caller_state_observation")

add("c30", "rand_r_posix", "example_value_posix_marker", context_label="posix_extension_caveat",
    rand_r_posix_not_iso=True, expected_success="success",
    expected_observation="rand_r_posix_not_iso_c_marker")

add("c31", "rand_r_quality", "synthetic_draw_rand_r_quality", context_label="posix_extension_caveat",
    rand_r_quality_not_guaranteed=True, expected_success="success",
    expected_observation="rand_r_quality_not_guaranteed_marker")

add("c32", "thread_race", "demo_counter_thread_race", context_label="thread_safety_not_tested",
    thread_race_not_run=True, expected_success="not_tested",
    expected_observation="thread_race_with_rand_not_run")

add("c33", "locking_marker", "fake_library_call_lock", context_label="thread_safety_not_tested",
    locking_not_quality_fix=True, expected_success="success",
    expected_observation="locking_rand_not_a_quality_fix_marker",
    expected_reason="HN comment: adding locks around rand made multithreading useless")

add("c34", "per_thread_state", "test_prng_state_per_thread", context_label="thread_safety_not_tested",
    per_thread_state_not_implemented=True, expected_success="not_tested",
    expected_observation="per_thread_rng_state_not_implemented")

add("c35", "project_prng", "example_value_project_prng", context_label="srand_policy",
    project_prng_not_implemented=True, expected_success="not_tested",
    expected_observation="project_local_prng_marker_not_implemented")

add("c36", "game_seed", "fake_game_roll_deterministic", seed_value=12345, draw_count=5,
    context_label="srand_policy", deterministic_game_seed_marker=True, expected_success="success",
    expected_observation="deterministic_game_seed_marker")

add("c37", "fuzzing_seed", "synthetic_payload_fuzz", seed_value=777, draw_count=5,
    context_label="srand_policy", fuzzing_reproducibility_marker=True, expected_success="success",
    expected_observation="fuzzing_reproducibility_marker")

add("c38", "library_internal", "fake_library_call_internal", seed_value=200, draw_count=5,
    context_label="hidden_state_caveat", library_internal_rand_marker=True, expected_success="success",
    expected_observation="library_internal_rand_call_marker")

add("c39", "fork_seed", "demo_counter_fork", context_label="portability_not_tested",
    fork_seed_not_tested=True, expected_success="not_tested",
    expected_observation="fork_process_seed_interaction_not_tested")

add("c40", "rand_state_serialize", "test_prng_state_serialize", context_label="portability_not_tested",
    rand_state_serialization_not_portable=True, expected_success="success",
    expected_observation="serialization_of_rand_state_not_portable_marker")

add("c41", "strtol_valid", "example_value_strtol_42", context_label="rand_policy",
    strtol_seed_valid=True, expected_success="success", seed_parse_input="42",
    expected_observation="atoi_strtol_seed_parsing_valid")

add("c42", "strtol_trailing", "example_value_strtol_junk", context_label="rand_policy",
    strtol_seed_trailing_junk=True, expected_success="error", seed_parse_input="123abc",
    expected_observation="strtol_trailing_junk_seed_rejected")

add("c43", "strtol_range", "example_value_strtol_range", context_label="rand_policy",
    strtol_seed_range_errno=True, expected_success="error", seed_parse_input="999999999999999999999",
    expected_observation="strtol_range_errno_seed_rejected")

add("c44", "negative_seed_cast", "demo_seed_negative", context_label="rand_policy",
    negative_seed_cast_caveat=True, expected_success="success", seed_parse_input="-1",
    expected_observation="negative_seed_cast_caveat_marker",
    expected_reason="srand takes unsigned int – negative input casting caveat")

add("c45", "unsigned_seed_width", "demo_seed_width", context_label="rand_policy",
    unsigned_seed_width_caveat=True, expected_success="success",
    expected_observation="unsigned_seed_width_caveat_marker")

add("c46", "shuffle_modulo", "sample_shuffle_modulo", seed_value=555, draw_count=10,
    context_label="modulo_bias_caveat", shuffle_modulo_marker=True, expected_success="success",
    expected_observation="shuffle_with_rand_modulo_marker")

add("c47", "dice_roll", "fake_game_roll_d6", seed_value=13, draw_count=20, modulo_n=6,
    context_label="modulo_bias_caveat", dice_roll_modulo_marker=True, expected_success="success",
    expected_observation="dice_roll_rand_modulo_marker")

add("c48", "security_token", "fake_entropy_label_token", context_label="crypto_not_tested",
    security_token_misuse_not_run=True, expected_success="not_tested",
    expected_observation="security_token_misuse_marker_not_run",
    expected_reason="do NOT use rand for security tokens")

add("c49", "password_reset", "fake_entropy_label_pwreset", context_label="crypto_not_tested",
    password_reset_token_misuse_not_run=True, expected_success="not_tested",
    expected_observation="password_reset_token_misuse_not_run")

add("c50", "csprng_alt", "fake_entropy_label_csprng", context_label="crypto_not_tested",
    csprng_alternative_not_used=True, expected_success="not_tested",
    expected_observation="csprng_alternative_not_used_marker")

add("c51", "openbsd_srand", "example_value_openbsd", context_label="portability_not_tested",
    openbsd_srand_deterministic_not_tested=True, expected_success="not_tested",
    expected_observation="openbsd_srand_deterministic_discussion_not_tested")

add("c52", "rust_core", "fictional_device_rust", context_label="portability_not_tested",
    rust_core_std_not_tested=True, expected_success="not_tested",
    expected_observation="rust_core_std_embedded_comparison_not_tested",
    expected_reason="HN debate: Rust core/std, embedded alternatives – not tested here")

add("c53", "double_promotion", "example_value_double_promote", context_label="portability_not_tested",
    double_promotion_not_tested=True, expected_success="not_tested",
    expected_observation="double_promotion_adjacent_footgun_not_tested",
    expected_reason="HN comment: accidental float→double promotion in embedded C – adjacent footgun, not tested")

add("c54", "cleanup_marker", "demo_counter_cleanup", context_label="rand_policy",
    cleanup_marker=True, expected_success="success",
    expected_observation="no_global_reset_except_srand_marker")

add("c55", "naive_negative", "example_value_naive_fail", context_label="naive_negative",
    naive_should_fail=True, expected_success="error",
    expected_observation="naive_rand_assumes_crypto_portable_unbiased",
    expected_reason="naive method assumes rand is crypto, unbiased, portable – should fail")

# write cases
os.makedirs(os.path.dirname(__file__) or ".", exist_ok=True)
with open(os.path.join(os.path.dirname(__file__), "cases.json"), "w") as f:
    json.dump(cases, f, indent=2)
print(f"Wrote {len(cases)} cases to cases.json")
