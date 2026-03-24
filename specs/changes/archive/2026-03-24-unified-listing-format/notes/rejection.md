## Rejected

Implementation was completed and git-reset by the author. The new format was too verbose compared to the original.

### Before (old format)

```
env-quy6 [open] - Assess if plant needs repotting
env-3w68 [open] - Select a new pot one or two inches wider <- [env-quy6]
```

### After (new format)

```
env-quy6 [open] :: Assess if plant needs repotting :: [tags: assessment]
env-3w68 [open] :: Select a new pot one or two inches wider :: [blocked-by: env-quy6] [tags: preparation]
```

### Verbosity sources

1. `[blocked-by: ...]` adds ~10 chars per line over `<-`
2. `[tags: ...]` is entirely new content shown by default on every line
3. `::` delimiters slightly wider than `-`

### Takeaways for a future attempt

- Tags should be opt-in (`--tags` flag), not shown by default
- `[blocked-by: ...]` may be the right label but the cost is real -- consider shorter alternatives like `[needs: ...]`
- The `<-` ambiguity problem is real but the cure was worse than the disease in terms of readability
- Could address the ambiguity through documentation alone (help text, agent rules) without changing the format
