# writing-th setup: hooks

`writing-th`'s "no prose before an approved argument map" gate is enforced by
two Claude Code hooks, not just written convention — without them, the rule is
just documentation.

## Apply the hooks to a consuming project

Option A — manual: open the project's `.claude\settings.local.json` and merge in
the `hooks` key from `settings.local.hooks.json` in this folder. If the project
already has a `hooks` key for something else, combine the `PreToolUse`/
`PostToolUse` arrays rather than overwriting.

Option B — scripted (still requires a manual review after):

```
.\merge-hooks.ps1 -SettingsPath "<project root>\.claude\settings.local.json"
```

This backs up the existing file first and only replaces the `hooks` key —
`permissions`, `skillOverrides`, `enabledMcpjsonServers`, etc. are left as-is.
It does not attempt a deep merge if the project already has a different
`hooks` key of its own — check the printed warning and the backup diff.
