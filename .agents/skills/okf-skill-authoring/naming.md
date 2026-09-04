---
type: Playbook
description: How the skill directory and `name` field are chosen. Read when creating or renaming a skill.
---

# Naming

The directory name is the skill's identity and, in Claude Code, its slash command. The `name` field matches the directory exactly, lowercase letters, digits, and single hyphens, no leading or trailing hyphen. Cross-runtime skill loaders reject a mismatch, and Claude Code uses the field as the display label.

Name the domain the skill governs: `python-development`, `okf-skill-authoring`, `kyzodb-messaging`. The name is specific enough that a reader can say which skills it does not cover. A name that describes the artifact rather than the domain (`guide`, `docs`, `notes`) or that would fit any skill in the repo (`best-practices`, `conventions`) fails that test.

Renaming a skill is a directory rename, a `name` field change, and, where a `.claude/skills/` symlink exists, a symlink rename, all in one change.
