---
title: "`x86` Timers"
tags: [microarch]
date: 2023-01-02
description: "Ready. Set. Go."

---

In my _Secure Processor Microarchitecture_ course at college, we were given an assignment on mounting a timing attack, and an evict+time attack on AES—specifically, the T-Table implementation found in OpenSSL. I won't get into the details of how to perform those attacks[^2], but I want to write about a few things I learnt while doing the assignment—how to acccurately measure clock cycles, upto a single clock cycle.

## High Resolution Timing in `x86_64`
Most—if not all—modern processors _need to_ have some method to capture timing differences of the order of a few clock cycles, which are usually used by games (input processing, in-game counters etc.), networking (to synchronize time with a server[^3]), and even cryptographic libraries (to generate random seeds).

In the assignment, I needed to measure the time taken by certain functions (something like the code shown below), determine whether there was a L1$ miss with which I could reverse the AES secret key. 

```c
start = time();
func();
end = time();
delta = end - start;
if (delta > THRESHOLD){
  ...
}

```
The times I need to measure are in the range of tens of clock cycles, so I cannot use implementations like `std::chrono` or `clock_gettime()` due to their overhead[^4].

### Enter `TSC`

> The time-stamp counter (TSC) is used to count processor-clock cycles. Each time the TSC is read, it returns a monotonically-larger value than the previous value read from the `TSC`. 
> — <cite>[AMD Programmer's Manual](https://www.amd.com/system/files/TechDocs/40332_4.05.pdf#G9.1031959)</cite>

However, there are a lot of hidden problems to this method:

1. The `TSC` isn't incremented on _every_ clock cycle. It is only incremented at _a constant rate_. DVFS and other power-saving techniques mean that the processor's clock frequency isn't constant at all times. So `RDTSC` doesn't accurately capture the _actual_ number of clock cycles. This problem can be mitigated using `cpupower(1)` to set the frequency governor to userspace and fix the frequency of the core. However, this does require root privileges.

2. There's a separate `TSC` for every physical core. So a process using the `RDTSC` instruction shouldn't migrate from one core to another (which the OS usually does for load-balancing)—or if it does, be within the same physical core, but on a different logical core. This is usually tackled by setting the affinity mask of the process/thread using `sched_setaffinity(2)` or `taskset(1)`.

3. Closely related to the above point is _process isolation_—context switches lead to wrong measurements. This means that, not only should a process run on a single core, but also, it _should be the only one running_ on the core. This also means that neither interrupts, nor the scheduler process itself should run on the core!! The fix for this turned out to be rather cumbersome[^5]—kernel commandline parameters `isolcpus`, `nohz_full` and `irq_affinity`.

4. However, even with the above kernel parameters, I wasn't able to isolate a few kernel threads from running on the isolated cores. I went down a deep rabbit hole before concluding to just go with it as `htop`'s time column showed 0:00.00 for those threads. If you're reading this and know how to isolate kernel threads from running on certain cores and dedicate those cores for just one userspace application, I'm curious.

### OOO Problems (geddit?)
Even with all the above, there's an inherent flaw in the `RDTSC` instruction itself—it isn't a serializing instruction, and due to the out of order nature of modern processors, it might actually be _executed before or after you actually want it to be executed_ in the program!! This had a trivial fix, by inserting a few memory fence (serializing) instructions before reading the `TSC`, something like below:

```c
inline __attribute__((always_inline))
uint64_t timestamp()
{
	uint32_t low_a, high_a;
	asm volatile ("lfence\n\t"
		  "mfence\n\t"
		  "rdtsc\n\t"
          "lfence\n\t"
		  "mov %%edx, %0\n\t"
		  "mov %%eax, %1\n\t"
		  : "=r" (high_a), "=r" (low_a)
		  :: "%rax", "%rdx");
	uint64_t aval = ((low_a) | (uint64_t)(high_a) << 32);
	return aval;
}
```

The 2 `MOV` instructions move the result from `EDX`:`EAX` into the locations we want to store them in. These will not be executed before the `RDTSC` instruction as there's a dependency on it.

> `LFENCE` does not execute until all prior instructions have completed locally, and no later instruction begins execution until `LFENCE` completes.
> 
> `MFENCE` performs a serializing operation on all load-from-memory and store-to-memory instructions that were issued prior the `MFENCE` instruction.
> — <cite>[Intel Programmer's Manual](https://cdrdv2.intel.com/v1/dl/getContent/671200)</cite>

## A more modern approach*
<sub><sup>* That works on Zen 2 and above platforms only</sub></sup>

I was going through the AMD Programmer's Manual—to look up how AMD recommends to use `RDTSC`—and I glanced upon another instruction: `RDPRU`. This allows access to processor-specific registers in _userspace_. And one of the registers it offers access to is the `APERF` register, which is incremented at the _actual clock frequency_ of the core. This means I should be able to mitigate Problem 1 with `RDTSC`—requiring root privileges to change frequency governor and set constant clock frequency. Fortunately, I have a laptop with a Ryzen 4800HS—which meant I could actually use this!!

The timestamping function is a bit different this time:

```c
#define RDPRU_ECX_APERF	1 		  /* Use APERF register in RDRPU */

inline __attribute__((always_inline))
uint64_t timestamp()
{
	uint32_t low_a, high_a;
	asm volatile("lfence");
	asm volatile("rdpru"
		     : "=a" (low_a), "=d" (high_a)
		     : "c" (RDPRU_ECX_APERF));
	asm volatile("lfence");
	uint64_t aval = ((low_a) | (uint64_t) (high_a) << 32);

	return aval;
}

```
The `lfence` instructions are needed here too. Passing 0 to `ECX` register would result in reading the `MPERF` register, which ticks at the _max clock frequency_ of the core.

## Results

I tried both methods—`RDTSC` as well as `APERF`—and found that on average the delta times measured using `APERF` were closer together, and I was able to find the distinguisher more easily. However, with `RDTSC`, there was a peculiar observation—the times measured always were in _steps of 29 cycles_. If that didn't make sense, let me explain.

With `APERF`:
> 364, 362, 363, 367, 493, 360, 362, 362 ... 365.

These were the various access times I received for accessing the probe array while reverse engineering the key. You can see that most of the times are close to 360, with exactly one access very far away—this array index is the value of the key byte itself.

However, with `RDTSC`, I observed the following:
> 358, 358, 387, 387, 503, 358, 387, 358 ... 387.

As you can see, while there's still a clear distinguisher, the values are in steps of 29 (or its multiples—503-387=4\*29; 387-359=29). I tried this repeatedly for different values of the key (which I had control over for the assignment demo), tried it at different frequencies set using `cpupower(1)`, but it always was a step of 29. I'm not sure why this happens, but hey, I was just happy that the attack finally worked :P.

[^2]: https://en.wikipedia.org/wiki/Timing_attack
[^3]: There's this wonderful podcast by Jane Street: https://signalsandthreads.com/clock-synchronization/
[^4]: `perf(1)` could've been used, but I wanted to keep it simple. ~~And I couldn't have written this post, could I?~~
[^5]: I hate rebooting my computer.
