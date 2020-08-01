#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <complex.h>
#define NCprintf(a)     (printf(#a " = "),Cprintf(a))
void Cprintf(complex double z)
{
    printf ("%f %+fi\n", creal(z), cimag(z));
}
int main(void)
{
    double complex z = 1 + 2i;
    double complex c;
    NCprintf(z);
    NCprintf(z * z);
    NCprintf(I);
    NCprintf(z * I);
    NCprintf(z + (4 + 2i));
    NCprintf(conj(z));
    printf ("cabs(z) = %f\n", cabs(z));
    printf ("carg(z) = %f\n", (double) carg(z));
    NCprintf(sin(z));
    NCprintf(exp(z));
    c = 3 + 4i;
    NCprintf(c);
    return (0);
}
