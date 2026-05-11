# Result Interpretation Guide

Interpretation must stay tied to observed artifacts.

## Principles

- Distinguish evidence from inference.
- Name the concrete files, histories, jobs, or outputs being interpreted.
- Explain what the result means operationally before offering scientific conclusions.
- Avoid strong biological claims unless the outputs support them.

## Useful Output Shape

For successful runs:

- what the workflow did
- which outputs matter most
- whether validation passed
- what caveats remain

For failed runs:

- failed phase or job
- strongest evidence for the cause
- likely fix
- whether rerun is needed

## Common Failure Categories

- missing or mismatched metadata
- wrong datatype
- paired-end files wired incorrectly
- incompatible reference genome naming
- tool parameter mismatch
- resource or quota failure
- empty or malformed input
