# Common Failure Modes

This document is a compact list of mistakes the orchestrator should actively avoid.

## 1. Treating the run like open-ended exploration

Wrong:

- “Let’s try a bunch of things and see.”

Right:

- run the pre-defined first-wave matrix
- preserve the gates
- rank the outcomes

## 2. Training before the baseline is valid

Wrong:

- launching training because the cluster is idle

Right:

- finish output gate
- finish benchmark smoke
- confirm parseability
- then train

## 3. Trusting training loss too much

Wrong:

- interpreting lower loss as better reasoning

Right:

- treat unexpectedly low loss on small data as a collapse warning
- require output-gate and benchmark confirmation

## 4. Allowing failed checkpoints downstream

Wrong:

- probing or benchmarking a checkpoint that failed output tests

Right:

- mark it invalid and stop there

## 5. Using a narrow benchmark as the only early signal

Wrong:

- concluding the strategy failed because a narrow benchmark is poor while the prompt contract is still shaky

Right:

- use HotpotQA / DROP / MuSiQue-style behavior checks first
- treat narrow or format-sensitive benchmarks as secondary until alignment is proven

## 6. Reusing stale probes

Wrong:

- keeping old probe outputs after changing dataset construction, prompt logic, extraction code, or recurrence capture

Right:

- rerun probes whenever the measurement path changes

## 7. Merging adapters into the base model

Wrong:

- merging for convenience
- evaluating merged weights as if they were still the clean base path

Right:

- keep base model immutable
- keep adapters separate

## 8. Confusing format learning with reasoning improvement

Wrong:

- assuming better formatting means better latent reasoning

Right:

- separate parseability from reasoning quality
- require external benchmark evidence and probe evidence

## 9. Letting one good number drive the story

Wrong:

- “This strategy won because one benchmark improved”

Right:

- require agreement across probe, behavior, and depth evidence

## 10. Switching methods instead of fixing the real blocker

Wrong:

- changing approach because a dependency, prompt path, or cache path failed

Right:

- fix the actual setup or measurement issue
- continue on the intended path

## 11. Losing restartability

Wrong:

- keeping logs only in terminal history
- waiting too long to commit and push

Right:

- write findings continuously
- push after each major phase
- preserve artifacts and decisions in the run repo

## 12. Forgetting the actual question

Wrong:

- acting as if the mission is “produce the best absolute model”

Right:

- identify the best next training direction efficiently and credibly
