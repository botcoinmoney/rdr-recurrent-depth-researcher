# Orchestrator Rules

Read this before doing anything else.

This is the operating contract for the orchestrator running the experiment on the GPU instance.

If you skip gates, weaken tests, or silently substitute a different path, you are no longer running the intended experiment.

## Mission

Produce a ranked, evidence-backed decision on the five first-wave recurrent-depth strategies under a `4xH100` budget, with valid probes, valid benchmark readouts, and clean logging.

## Absolute Rules

### 1. Do not burn GPU time before the baseline gates pass

Before any training:

- validate the environment
- validate the dataset path
- run baseline output gate
- run standard benchmark smoke gate

If those fail, stop and fix them first.

### 2. Never merge adapters into the base model

This includes:

- LoRA merge for convenience
- writing over the original model path
- producing a “merged checkpoint” as the working baseline

Keep:

- base model immutable
- adapters versioned separately
- evaluation scripts explicitly pointing to `base + adapter`

### 3. The probe is primary, but only when valid

Do not cite probe movement unless the run used:

- the current probe dataset
- current hidden-state extraction path
- grouped or challenge-disjoint splits when applicable
- the specified recurrence depths

If the measurement path changed, rebuild and rerun.

### 4. Behavioral evals must report parseable rate

Every benchmark artifact must report:

- total examples
- parseable examples
- parseable rate
- task score

Without that, you cannot separate reasoning failure from output-format failure.

### 5. DACR-Bench is secondary until prompt/output alignment is explicitly proven

DACR-Bench is useful, but it is not the primary first-wave decision metric if the prompt contract is still unstable.

Primary first-wave behavior readouts:

- HotpotQA
- DROP
- MuSiQue if available

### 6. Collapse overrides everything

Treat the following as collapse-danger:

- loss dropping much faster than expected into a memorization regime
- repetitive delimiters
- prompt echo
- coherent simple completion but broken reasoning-format output
- benchmark collapse relative to baseline

If collapse indicators appear:

1. stop that variant
2. mark it invalid
3. log the event immediately
4. restart from the clean base path

### 7. One metric never implies success

Do not claim success from:

- one benchmark
- one good AUC
- one depth
- one checkpoint

Require alignment across:

- probe evidence
- behavioral evidence
- depth-scaling behavior
- variant comparison

## Required Read Order

1. `README.md`
2. `RULES.md`
3. `docs/H100_SETUP.md`
4. `docs/RESEARCH_SYNTHESIS.md`
5. `docs/MEASUREMENT_AND_GATES.md`
6. `docs/EXECUTION_PLAYBOOK.md`
7. `docs/HANDOFF.md`

## Run Discipline

### Before touching GPUs

1. create the live private run repo
2. copy templates into it
3. commit the initial state
4. run environment preflight
5. run config validation

### During runs

- log every material event in `findings.md`
- wake on cadence
- do not launch duplicate jobs
- do not treat missing artifacts as implied success
- push often to the private run repo

### After any failure

- inspect the exact failure
- fix the exact cause
- document the fix
- rerun only the affected phase

Do not “work around” the issue by switching methods unless the method switch is already in the decision tree.

## Wake Cadence

- setup/bootstrap: every 2 minutes
- dataset build: every 5 minutes
- benchmark eval: every 10 minutes
- training: every 5 minutes
- output gates: every 2 minutes
- any exit or failure: immediate follow-up

## Required Logging Shape

Every material entry in the live run repo should use:

```md
### YYYY-MM-DD HH:MM UTC - [Phase] [Action]

**Status**: running | complete | error | aborted
**Artifacts**:
- path

**Metrics**:
- metric: value

**Decision**:
- continue | stop | rerun | escalate | demote

**Why**:
- short paragraph
```

## First-Wave Success Definition

Success means you can answer:

`Which of the five strategies shows the strongest credible signal for shaping recurrent hidden-state geometry for natural-language multi-hop reasoning, and why?`

Anything weaker should be reported as incomplete, not successful.

