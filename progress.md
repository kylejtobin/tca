# Progress: the parser crossing

## Where it stands

The parser crossing is paused. No parser code is in the skill.

In place and agreed:

- `SKILL.md` names the reading and writing of a format in `parser/` as the only functions besides `interpret` and the `main.py` callback.
- `SKILL.md` states the crossing rule: a dictionary or JSON constructs a model; a format that is neither is read by a maintained library that yields one; only a format no library yields one from is read by a format type in `parser/`.
- The file table has no `parser/` row; it gets one with `parser.md` when the page exists.
- smell-check does not scan `parser/`, and fails `PARSER-IMPORT` on any import of `parser` outside `integration/<system>/model.py`.

## What to build

The example is the payment provider's settlement report: a fixed-width text file, one settled charge per line (charge id, amount, currency). The example world is ours to define; define its API and meaning openly.

1. `parser.md`, with this sentence at the top and code only below it:

   > You write a parser only when what arrives is neither a dictionary nor JSON and no maintained library yields one from it. In that case you write exactly one format type per format, in `parser/<format>.py`, and every integration that receives that format uses that same format type.

2. The format layer, `parser/fixed_width.py`: `FixedWidth` as a real Pydantic custom type. Its core schema parses, types and writes. This is the layer `Settlement` composes on.
   - `FixedWidth` is a `BaseModel` holding its grammar (a `Grammar` scalar: a pattern whose named groups are the record's field names or aliases).
   - It attaches through `GetPydanticSchema` from a property, because `BaseModel` already owns `__get_pydantic_core_schema__`.
   - Its validation is one `chain_schema`: text, then the grammar turning each line into a record of named strings, then each record constructed in string mode by the record class, `typing.get_args(source)[0].model_validate_strings(record)`.
   - Its serialization is `plain_serializer_function_ser_schema`, rendering each record dumped by alias back into the format.

3. The foreign model, `integration/payments/model.py`. The integration only annotates; it never calls the parser.
   - `SettledCharge`: charge, amount, currency, under the provider's names.
   - `Settlement(RootModel[Annotated[tuple[SettledCharge, ...], FixedWidth(...).format]])`.
   - `Settlement.model_validate(text)` is the whole crossing. `Settlement.model_dump()` is the report text.

4. The effect side, decided openly before it is written:
   - the settlement API: its resource and what is sent to it;
   - the domain fact that authorizes reading a settlement, and its action;
   - the domain outcome reading a settlement produces, so the interpreter returns a domain fact, not the foreign `Settlement`.

5. smell-check fails on any validator or `__get_pydantic_core_schema__` outside `parser/`. This was agreed and not built.

## Hard choices to face, not route around

- Strict scalars refuse `"0000003780"` from Python input. Handing the parsed records to `handler(source)` validates them as Python objects and fails. The record step must be string-mode construction inside the chain. Do not replace it with a wrapper class, a layout subclass, or a parser call from outside the type.
- Writing back belongs to the same core schema, not to a second class.
- The settlement API, its meaning, and the authorizing fact are design decisions in our example world. Decide them, state them, then build. "No evidence" is not a reason to stop or to invent silently.
- When an agreed approach fails, stop and report the failure with its evidence. Do not redesign.

## Tested facts (Pydantic 2.13.5)

- `model_validate_strings` constructs a strict `Amount` from `"0000003780"`.
- `model_validate_strings` accepts mappings of strings only, not tuples or lists.
- A `chain_schema` with a plain validator function followed by `handler(source)` validates the function's output as Python input; strict scalars reject the strings.
- `re.match(f"(?:{grammar})?", line).groupdict()` gives `None` values for a non-matching line, and `model_validate_strings` rejects them with `ValidationError`.
- A fixed-width template `"{id:<10}{amt:010d}{cur}\n"` with `format_map` round-trips the report text exactly.

## Open outside the parser

- Strict `model_validate` refuses a dictionary decoded from JSON (`'usd'` is not a `Currency`, a list is not a tuple). The checkout's dictionary crossing, `CheckoutRoute.model_validate(await request.json())`, has this problem and is unchanged.
