# Candidate v2 Corpus-v1 exploratory gates — results

Status: exploratory discovery only; no Candidate v2 selected or frozen. Run: https://github.com/yigitcan-ozturk/pamir/actions/runs/36243226306 (successful execution).

## Population and baseline
50 SHA-verified Corpus v1 public PX4 logs: 33 source-labelled healthy controls, 6 source-labelled incidents, 11 unknown. Frozen threshold 7.0: healthy material roots 16/33; incident material roots 3/6; unknown roots 10/11.

## External post-selection suppression proxies

| Gate applied to frozen estimation root | Healthy roots | Incident roots | Unknown roots | Incident roots lost |
| --- | ---: | ---: | ---: | --- |
| Frozen (no gate) | 16 | 3 | 10 | 0 |
| >=2 same-signal event timestamps | 1 | 1 | 0 | 2 (FV-E003, FV-I001) |
| >=2 timestamps spanning >=250ms | 1 | 1 | 0 | 2 (FV-E003, FV-I001) |
| >=4 distinct deviation signals in forward 3s | 15 | 3 | 10 | 0 |
| >=2 timestamps and >=4 distinct signals | 1 | 1 | 0 | 2 (FV-E003, FV-I001) |

The distinct-signal gate suppressed healthy case FV-H002 only. Distinct deviation signals do not demonstrate independent physical sensor corroboration.

## Interpretation and next steps

The temporal-persistence proxies fail incident-retention requirements on Corpus v1. The four-distinct-signal proxy produces only one fewer healthy root while preserving three incident roots; this is insufficient to claim robust improvement. These are post-selection suppression proxies; they do not model root migration, fallback, or a real candidate selector. No threshold or frozen v0.1 baseline was changed. Independent Holdout v1 is spent and must not be used for v2 development.

Next discovery: use Corpus v1 only to inspect source-channel lineage and mechanism-specific output_tracking_error cases; implement and evaluate a true external reselecting candidate (including migrations and incident losses) before freezing its specification. Any subsequent independent test requires a new source-labelled, UUID/SHA-deduplicated holdout.
