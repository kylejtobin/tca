# Findings from the reference agent

What building the TCA agent with Pydantic AI showed about the `python-dev-tca` skill, and how each finding was resolved in the skill, its examples, the registrar, the agent and the checker.

## Resolved

| Conflict | The distinction it revealed | Resolution |
|---|---|---|
| A strict float rejected `"0.5"` from the environment, so config was lax and the shop's own environment could not construct it | A representation is not a value: the environment is text, and text has its own validation mode | Every class is strict, and pydantic-settings' source decodes the environment's text against each field's type, a strict float and a strict enum included, so no class is lax for the environment's sake |
| A frozen provider held the library's mutable `UsageLimits` | Immutable configuration, the library's contract, and an execution's resources are three things | The provider holds nothing of it: the library's limits are its defaults, and a caller's usage is an execution resource passed to `interpret` |
| `RunUsage`, `CancellationToken` and their `None` defaults conflicted with "no None, no parameters" | Persistent meaning is held; an execution's mechanics are passed | Keyword-only arguments of `interpret` and the root callbacks, in the library's types, defaulting to `None`, the library's own word for absence |
| Interpreters used a client they never released, relying on `max_keepalive_connections=0` | A capability has a lifetime, and the effect that uses it owns it | `interpret` may stand within the one `async with` that acquires its capability; the keepalive workaround is gone |
| "At most one per aisle" contradicted the tunable `per_aisle`, and `IndexGroups.matches` flattened the index's groups | The domain means grouped matches | `Aisle`, `AisleMatches`, `Aisles` and `NoAisles`, with rejection predicates for each product once and each aisle once; the index's group is validated to hold only its aisle's hits |
| `Decline` promised a reason while `DeclineReasons` could be empty; `Fqdn` and `DomainName` admitted names no registry accepts | A docstring, a type and the valid states must agree | `DeclineReasons` holds at least one; `Fqdn` has the written form; a domain name is at most 253 characters |
| The five-layer ladder failed against its own examples | Alternatives and collections are shapes at every layer; crossings hold the domain | Three layers, Scalar, Value and Thing, placed by fields at their own layer or above; alternatives and collections take their members' layer; crossings hold the domain and are held by none |
| Provider addresses, keys, the index's names and the registrar's status words lived in the domain | Ownership follows whose meaning and rules define a type | Integration-owned scalars live in their system's `model.py`; HTTP vocabulary handed to a library is a literal argument; the domain imports nothing outside itself, enforced by import-linter |
| The JSON-only entry rule was false for config and for the agent's output | Who authors the contract decides what validates it | Data is validated once, by the type that stands for its contract, in its representation's mode; a foreign record precedes the domain fact when another system authors the contract |
| The regex checker missed multi-line signatures, flagged docstrings, and could not admit native controls | Mechanical rules follow the specification, not lines of text | An AST checker by zone, with one valid tree and an adversarial fixture per label, each held to its exact labels |
| Moving image tags and an archive-installed tool | A reproducible build fixes every input by content | Images pinned by version and digest, the lockfile checked, nothing installed from an archive |
| The agent's provider could not derive the agent: its tools are interpreters, and a provider precedes interpreters | A library that calls back into the program is composed by the interpreter that acquires it, from the providers' clients and the interpreters it calls back; a system reached two ways is two providers from one deployment statement | The agent's provider derives one capability, everything the agent is but its model and its tools; the answering and chat interpreters compose the agent with the check interpreter's `interpret` as its tool and acquire it; the workspace reached as a shell is the check's provider, constructed from the workspace the deployment named |

## Held

- Structured output requires an object schema: `output_type` cannot be a `RootModel` scalar, so `Answer` is the smallest domain object around the words.
- A provider holds what the deployment names and the library does not read for itself; Pydantic AI's providers read their endpoint and credentials for themselves, and the library defaults its limits, thinking and instrumentation, so the provider holds a model name and the agent has no other setting. The restatement of that surface in our types, built before any deployment set it, is what the pass before this one spent itself reconciling.
- A provider derives its client per crossing, so the library's `override` on one agent reaches no run; a test hands the library its model where the library infers the name `test`.
- Every failure path is the library's own exception; no domain failure type was needed.
- `ruff format` rewrites the Python inside the skill's markdown pages when run over the package, so it is run over the Python directories only.

## Open

- The checker skips relative imports when it checks that a domain imports nothing outside itself, so `from ...integration import x` in a domain file is not a hit; import-linter's contracts hold that line meanwhile.
- The checker checks fields and config only on classes whose base is `BaseModel`, `RootModel` or `BaseSettings`; a plain class, or a subclass of one of the program's own models, is not checked for the rule that every class is one of the three, strict and frozen.
- Whether `Recommending`'s tuning, expressed in the index's similarity scale, is the domain's policy or the index's parameter.
- A construct page's later code blocks omit imports their first block shows, so the checker reads assembled pages as holding unknown classes; the pages are fragments, not files.
