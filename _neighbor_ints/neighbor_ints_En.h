#ifndef NEIGHBOR_INTS_EN_H
#define NEIGHBOR_INTS_EN_H

#include <stddef.h>

void cythonFunction(
    const double *P,
    const size_t *t,
    const double *normal,
    const double *center,
    const size_t *neighbor,
    const double *area,
    size_t N,
    size_t T,
    size_t M,
    int gauss,
    double *IE,
    double *IC
);

#endif