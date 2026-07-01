
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
#include <limits.h>

#ifdef __has_include
#  if __has_include(<features.h>)
#    include <features.h>
#  endif
#endif

/* rand_r availability check */
#if defined(_POSIX_C_SOURCE) && _POSIX_C_SOURCE >= 200112L
#  define HAVE_RAND_R 1
#elif defined(_XOPEN_SOURCE) && _XOPEN_SOURCE >= 500
#  define HAVE_RAND_R 1
#elif defined(__unix__) || defined(__linux__) || defined(__APPLE__)
#  define HAVE_RAND_R 1
#endif

int main(int argc, char **argv) {
    if (argc < 2) {
        printf("usage: %s <op> [args...]\n", argv[0]);
        return 2;
    }
    const char *op = argv[1];

    if (strcmp(op, "randmax") == 0) {
        printf("RAND_MAX=%d\n", RAND_MAX);
        return 0;
    }

    if (strcmp(op, "draw") == 0) {
        if (argc < 4) return 2;
        unsigned int seed = (unsigned int)strtoul(argv[2], NULL, 10);
        int n = atoi(argv[3]);
        if (n < 0) n = 0;
        if (n > 10000) n = 10000;
        srand(seed);
        printf("seed=%u draws=", seed);
        for (int i = 0; i < n; i++) {
            if (i) printf(",");
            printf("%d", rand());
        }
        printf("\n");
        return 0;
    }

    if (strcmp(op, "same_seed_repeat") == 0) {
        if (argc < 4) return 2;
        unsigned int seed = (unsigned int)strtoul(argv[2], NULL, 10);
        int n = atoi(argv[3]);
        if (n < 0) n = 0;
        if (n > 10000) n = 10000;
        srand(seed);
        int *first = (int*)malloc(n * sizeof(int));
        if (!first && n > 0) return 1;
        for (int i = 0; i < n; i++) first[i] = rand();
        srand(seed);
        int match = 1;
        for (int i = 0; i < n; i++) {
            int v = rand();
            if (v != first[i]) { match = 0; break; }
        }
        free(first);
        printf("same_seed_repeat=%s\n", match ? "yes" : "no");
        return 0;
    }

    if (strcmp(op, "library_disturb") == 0) {
        if (argc < 4) return 2;
        unsigned int seed = (unsigned int)strtoul(argv[2], NULL, 10);
        int n = atoi(argv[3]);
        if (n < 0) n = 0;
        srand(seed);
        /* draw n, with a fake library call in the middle consuming 1 draw */
        printf("draws=");
        for (int i = 0; i < n; i++) {
            if (i) printf(",");
            if (i == n/2) { /* fake library call */ (void)rand(); }
            printf("%d", rand());
        }
        printf("\ndisturbed=yes\n");
        return 0;
    }

    if (strcmp(op, "modulo_bias") == 0) {
        if (argc < 3) return 2;
        int mod = atoi(argv[2]);
        if (mod <= 0) { printf("error=modulo_zero\n"); return 1; }
        long rm = RAND_MAX;
        long buckets = mod;
        long full_cycles = (rm + 1) / buckets;
        long remainder = (rm + 1) % buckets;
        printf("RAND_MAX=%ld mod=%d full_cycles=%ld remainder=%ld biased=%s\n",
            rm, mod, full_cycles, remainder, remainder ? "yes" : "no");
        return 0;
    }

    if (strcmp(op, "bucket_count") == 0) {
        if (argc < 5) return 2;
        unsigned int seed = (unsigned int)strtoul(argv[2], NULL, 10);
        int draws = atoi(argv[3]);
        int mod = atoi(argv[4]);
        if (mod <= 0 || mod > 1000) return 1;
        if (draws < 0 || draws > 100000) draws = 1000;
        srand(seed);
        int *buckets = (int*)calloc(mod, sizeof(int));
        if (!buckets) return 1;
        for (int i = 0; i < draws; i++) {
            int r = rand();
            buckets[r % mod]++;
        }
        printf("buckets=");
        for (int i = 0; i < mod; i++) {
            if (i) printf(",");
            printf("%d", buckets[i]);
        }
        printf("\n");
        free(buckets);
        return 0;
    }

    if (strcmp(op, "strtol_seed") == 0) {
        if (argc < 3) return 2;
        const char *s = argv[2];
        char *end = NULL;
        errno = 0;
        long v = strtol(s, &end, 10);
        if (errno == ERANGE) { printf("result=range_error errno=ERANGE\n"); return 0; }
        if (end == s || *end != '\0') { printf("result=trailing_junk\n"); return 0; }
        printf("result=ok value=%ld unsigned_value=%u\n", v, (unsigned int)v);
        return 0;
    }

#ifdef HAVE_RAND_R
    if (strcmp(op, "rand_r_test") == 0) {
        if (argc < 3) return 2;
        unsigned int state = (unsigned int)strtoul(argv[2], NULL, 10);
        int n = argc > 3 ? atoi(argv[3]) : 5;
        if (n < 0) n = 0;
        if (n > 10000) n = 10000;
        printf("rand_r_available=yes draws=");
        for (int i = 0; i < n; i++) {
            if (i) printf(",");
            printf("%d", rand_r(&state));
        }
        printf(" final_state=%u\n", state);
        return 0;
    }
#endif

    printf("error=unknown_op op=%s\n", op);
    return 2;
}
