#include <stdio.h>
#include <stdint.h>
#include <time.h>

int main(int argc, char *argv[]) {
  const uint64_t  ui8Sleep = 500000;

  struct timespec tsStart;
  struct timespec tsPlan;
  struct timespec tsActual;

  uint64_t        ui;
  clock_gettime(CLOCK_MONOTONIC,&tsStart);
  ui = (uint64_t)tsStart.tv_nsec + ui8Sleep;
  tsPlan.tv_sec  = tsStart.tv_sec + (time_t)(ui/1000000000);
  tsPlan.tv_nsec = (long)(ui%1000000000);
  clock_nanosleep(CLOCK_MONOTONIC,TIMER_ABSTIME,&tsPlan,NULL);
  clock_gettime(CLOCK_MONOTONIC,&tsActual);

  ui = (uint64_t)tsActual.tv_sec*1000000000L+tsActual.tv_nsec
     - (uint64_t)tsPlan.tv_sec  *1000000000L-tsPlan.tv_nsec;
  printf("scheduled sleeping time: %lu[ns]\n",ui8Sleep);
  printf("actual sleeping time   : %lu[ns]\n",ui8Sleep+ui);

  return 0;
}
