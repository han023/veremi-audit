# What replaced the negative result

The original paper reported a negative result: naive protocols do not inflate AUC,
mean inflation $-0.012$ over eight archives. That test was invalid. Its "pseudonym
leak" feature was derived from the salted hash of the pseudonym, which by
construction carries no leakage. See `10_verification_audit.md` section C1.

The replacement is `exp9_cascade.py`: one detector, seven protocols, each removing
exactly one advantage. Five seeds per stage; the spread across seeds is reported
beside every mean, because it turns out to matter more than the effects.

## The stages

| Stage | What changes | Why it is there |
|---|---|---|
| S0 | ground-truth aggregation, real pseudonym feature, random $k$-fold, native 30 % | reconstructs Azam 2022, the most-cited recent ML paper on this data |
| S1 | pseudonym feature removed | isolates the encoding artefact |
| S2 | aggregation keyed on what a receiver sees | the partition must now be inferred |
| S3 | vehicle-disjoint split, asserted at run time | no vehicle in both folds |
| S4 | prevalence subsampled to 3 % | a deployment-plausible operating point |
| S5 | transmission times jittered by $U(-0.25, 0.25)$ s | the attacker's free escape |
| S6 | message-rate features dropped | forces the model onto kinematics |

## Result

AUC, mean over five seeds. Six of eight archives never move.

| Stage | GridSybil dense | GridSybil sparse | Other six archives |
|---|---|---|---|
| S0 published | 0.998 | 0.999 | 1.000 |
| S1 $-$ pseudonym | 0.997 | 0.999 | 1.000 |
| S2 $-$ ground-truth key | **0.937** | **0.936** | 1.000 |
| S3 $+$ disjoint split | 0.931 | 0.934 | 1.000 |
| S4 prevalence 3 % | 0.893 | degenerate | 1.000 |
| S5 $+$ jitter | 0.834 | degenerate | 1.000 |
| S6 $-$ rate features | 0.843 | degenerate | 1.000 |

Seed spread: 0.000 at S0-S2, 0.006-0.009 at S3, then **0.088 to 0.135** from S4 on.

## What the cascade actually supports

**Ground-truth aggregation is the leak that matters.** Removing it costs 0.060 and
0.064, against a seed spread of 0.002. That is the only unambiguous drop in the table.

**The pseudonym feature adds nothing.** Removing it costs 0.0006. This confirms the
original negative result, but now on an honest test rather than a hashed one. The
reason is that the pseudonym is redundant when the ground-truth key is already
supplying the partition.

**The vehicle-disjoint split costs a little.** 0.006 and 0.002, consistent in sign
across both densities but close to the seed spread.

**Below 3 % prevalence the archive cannot be evaluated.** The two sparse archives go
degenerate: a disjoint test fold holds fewer than five attacker vehicles. On the
dense archive the seed spread rises to 0.088, so S4-S6 differences cannot be
attributed to the controls. We say so rather than reading the drop as an effect.

**The trivial baseline is the uncomfortable column.** On all four denial-of-service
archives the untrained scalar also reaches 1.000, so the learned model contributes
exactly nothing. On GridSybil it beats the scalar by 0.28, which is the one place
the benchmark still measures something.

## Where jitter was actually measured

The cascade's S4 to S5 drop (0.893 to 0.834) sits inside a 0.13 seed spread and
must not be read as a jitter effect. Two cleaner measurements exist.

**On the per-identity task**, at native prevalence where the seed spread is 0.007
(`exp10_sensitivity.py`): AUC 0.927 with no jitter, 0.916 at half a second. Jitter
costs about 0.011. The rate gap between a 1 Hz beacon and a 50 s ghost survives it.

**On the pairwise linkage task**, jitter is decisive
(`v4_timing_distributions.py`). Phase AUC falls from 0.81-0.88 to 0.55-0.58 on the
denial-of-service families, and from 0.63-0.64 to 0.56-0.58 on GridSybil. All
separations are significant beyond $p = 10^{-8}$ before jitter.

Two shortcuts, two different escapes. The paper now says which is which.

## The phase mechanism, corrected

The original text claimed sibling identities have $\Delta t \bmod 0.5$ with median
$7\times10^{-6}$. The implemented feature is $|\mathrm{median}(\Delta t \bmod 1.0) - 0.5|$,
and measuring it per family shows the mechanism is family-dependent.

| Family | sibling median | unrelated median | implied offset |
|---|---|---|---|
| DoSRandomSybil | $2.8$--$3.0\times10^{-6}$ | 0.245--0.250 | exactly 0.5 s |
| DoSDisruptiveSybil | $2.7$--$3.1\times10^{-6}$ | 0.253--0.258 | exactly 0.5 s |
| GridSybil | 0.1667 | 0.250--0.258 | exactly 1/3 s |

Ghosts round-robin the attacker's transmit slot. The offset is the beacon period
divided by the identity count: one half for the hundred-identity families as they
pair up, one third for GridSybil attackers holding three identities. The
$7\times10^{-6}$ figure was roughly right for the denial-of-service families and
wrong as a universal statement.
