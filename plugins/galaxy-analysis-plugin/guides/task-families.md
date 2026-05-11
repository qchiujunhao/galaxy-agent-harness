# Workflow Classes and Validation Profiles

The plugin supports general Galaxy workflows. The named families below are validation profiles, not hard support boundaries.

If a request does not fit a named profile, classify it as `general_galaxy_workflow` and use the generic workflow path.

Do not refuse an analysis only because it is outside the named profiles. Named profiles add stronger defaults and validation checks; they are not support limits.

## General Galaxy Workflow

Typical inputs:

- GitHub repositories
- Galaxy histories
- workflow descriptions
- methods sections
- local datasets
- existing Galaxy workflow files

Expected outputs:

- a Galaxy history with executed steps where execution is possible
- produced datasets, collections, reports, or workflow artifacts
- a reproduction or analysis report
- a validation summary

Validation focus:

- every planned step has an observed Galaxy job, output, or explicit skip reason
- output datasets exist, are non-empty where applicable, and have plausible datatypes
- tool ids, versions, parameters, and history ids are recorded
- assumptions and deviations are explicit
- task-specific claims are limited when no specialized profile applies

Use this class for any workflow outside the specialized profiles below.

When reporting generic validation, state which checks are generic structural checks and which specialized scientific checks were not available.

## Short-Read QC and Trimming

Typical inputs:

- FASTQ or FASTQ collections
- paired-end or single-end layout
- optional adapter settings

Expected outputs:

- raw QC report
- trimmed reads
- post-trim QC report
- optional MultiQC summary

Validation focus:

- paired-end files remain paired
- output read files are non-empty
- QC summaries are readable
- trimming settings are recorded

## Count-Matrix Differential Expression

Typical inputs:

- count matrix
- sample metadata
- contrast or grouping definition

Expected outputs:

- normalized or modeled results
- differential expression table
- diagnostic plots where available

Validation focus:

- metadata samples match matrix columns
- contrast is explicit
- result table has identifiers, statistics, and adjusted p-values when available
- no silent sample dropping

## Host Contamination Removal

Typical inputs:

- reads or read collections
- host reference or declared host organism

Expected outputs:

- filtered reads
- host/non-host classification or alignment summary
- optional QC report

Validation focus:

- host reference is recorded
- read pairing is preserved
- filtered output exists and is readable
- summary counts are plausible

## Simple ATAC-Seq Peak Calling

Typical inputs:

- paired-end reads or aligned BAM
- reference genome
- optional blacklist and peak-calling settings

Expected outputs:

- filtered alignments
- peaks
- signal tracks where supported
- QC metrics

Validation focus:

- paired-end assumptions are explicit
- mitochondrial and duplicate handling is recorded
- peaks are non-empty when biologically plausible
- signal and peak outputs use consistent genome naming

## History and Failure Explanation

Typical inputs:

- Galaxy history id
- job id
- dataset id
- stderr/stdout

Expected outputs:

- explanation of what ran
- failure boundary or output interpretation
- recommended remediation

Validation focus:

- identify evidence versus inference
- cite concrete job/tool/dataset metadata when available
- do not overstate certainty from partial logs
