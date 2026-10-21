# TCA

## Positioning

For the developer who builds the backend services of a business, the ones with rules, external parties and decisions, and who writes them today as a controller, a model, a validator, a mapper, a service, a repository and a container, TCA is a backend application framework in which the service is written as types and nothing else. Unlike every framework on that shelf, it checks the logic and not only the edges: there is no function between what arrives and what leaves, so the type checker reads the whole program and the program refuses what the business does not allow. It is built in Python, on Pydantic.

## The customer

One person: the developer who builds business services and has shipped a bug from a service method that passed the type checker and the tests. They learned the layered habit in Spring or ASP.NET, or in its Python copies. They choose their own tools, read alone, and judge by trying.

The same program serves five others, with nothing written for any of them:

- the developer on day one, with the business written and no server, who runs it from the shell and sees it answer;
- the operator who replays one request against staging without reading the code;
- the integrator who reads, in the API document, the descriptions the developer wrote on the fields;
- the reader who knows the business and not the code, who confirms the program says the business;
- the reasoning model that writes the service, judged by the same checker as a person.

## The problem

In the layered habit every layer has a tool that checks it except the one that matters. The framework validates what arrives. The database holds the schema. The container checks the wiring. The service, where every rule, every call and every decision lives, is checked by nothing but tests. The same model is written three times, with a mapper between each pair. The schema and the documentation are copies, and copies drift. The bugs that reach production come from the one layer no tool can see, and the tests exist to see what the compiler cannot.

## The promise

Each of these is a commitment, and each could be proven false.

- A value the business does not have cannot exist in the program. A rule is a type, and the wrong value has no type.
- The type checker reads the whole program. There is no service, no handler and no function between what arrives and what leaves.
- A program that is wired wrong does not start. A question nothing answers, a value nothing produces, or two things that each need the other is named, in the developer's own names, before anything runs.
- The developer says each thing once, and says only the business. Nothing in the program exists for the framework.
- Nothing is ordered. Each thing exists when what it is made of exists, and things that need nothing from each other happen together.
- The command line, the API and the documentation are one definition, read from the types. Choosing one or both changes nothing the developer wrote, and nothing drifts because nothing is a copy.
- There is one way to fail. A value outside the business is refused by name, the same way from the shell and from a request body. A party that does not answer raises its own client's error. Nothing else fails, because nothing else runs.
- A party's refusal is an answer, not an exception, and it reaches the caller as a reply.
- Every request is a trace named in the developer's words, one span per party asked, with no contents recorded.

## The scope

What it is: a backend application framework. It owns the configuration, the connections, the lifecycle, the wiring, the request boundary, the interfaces and the trace. It also owns the logic, because the logic is types.

What stays the developer's: Pydantic, the strict type checker, the HTTP server, the database, the trace exporter.

What it refuses to be: a validation framework, because validation is Pydantic's; a workflow engine, because there is no step, stage or plan; a DSL, because every construct is one Pydantic already documents; a handler framework, because there is no function between request and reply; a command-line framework, because each thing the program does is already the command.

There is no escape hatch inside a program. The only code that speaks to another system is the framework's, one piece per transport, and a program never contains it. Anything a program cannot express is a missing type or a missing transport, and that is a defect in the framework.

## The principles

A program is nothing but a true description of a business, and it runs because it is true.

The measure of every decision: the developer says less, says it once, and says only their world. A design that makes the developer say more, or say anything for the framework, is wrong even when it works.

Why it is built this way. Types made the machine able to hold what the developer means, and every framework stopped them at the edges. TCA takes types through the middle, so the program is the statement of what exists in the business and what follows from what, and the statement is what runs. And because the program is a world that refuses what is false, a mind can be let into it, a person's or a model's, and its errors cannot run. The wrong program cannot be written. The business is the program. Judgment can be put in production.

The defect rules. Anything in a program that exists for the framework is a defect in the framework. Any behavior in the framework that the developer should have declared is a defect in the framework. Any failed observation below is a defect in the framework, never in the program.

## The evidence

The promise is kept when each of these is observed on any program written against the framework.

- Every function in a program is a property of a type or a value computed from one.
- The strict type checker reports nothing.
- Removing the one thing that receives a party's answer stops the program at startup, naming that answer.
- A developer who has read Pydantic's documentation and one program writes the next operation without opening the framework.
- A reader who knows the business names what each type is from its name and description.
- The framework has no public types of its own, and one entry per interface.
- The program's help lists every operation, every field with its description, and every variable the deployment sets, from the program alone.
- The same request answered from the shell and over HTTP gives the same body.
- An operator replays a request against an environment without reading code.
- The served API document and the shell's help show the same fields and the same descriptions.
- A value outside a rule is refused the same way from the shell and from a request body, naming the field and nothing else.
- The reference for every operation, every answer and every variable is assembled from the program.

## The category and the competitors

The shelf is backend application frameworks: Spring Boot, ASP.NET Core, NestJS, Django, Rails. Each gives a checked edge and an unchecked middle. Against all of them the difference is one sentence: TCA has no middle.

The strongest competitors are the ones that can nearly say the middle is checked.

- **Effect**, in TypeScript. Dependencies, errors and services live in the type and are resolved by layers that fail at compile time when one is missing. Effect still runs your functions. TCA runs your types.
- **ASP.NET Core with F#.** The strongest checker on the shelf, and a community that already models a business as states that cannot be represented wrongly. They hold the ideology and the framework in separate hands. TCA holds them in one.
- **Spring Boot.** The container resolving a graph of types is TCA's startup proof and its run, and every Spring architect will say so. The container stops at the service object and hands control to a method. TCA does not stop.
- **ZIO**, in Scala. The compile-time proof of a dependency graph, done first and done rigorously. The proof wires the program; it is not the program running.
- **Servant**, in Haskell. The API is a type and every handler is checked against it, so the interface is defined once and everything is derived. That is half the promise. The other half, no handler at all, is where it stops.

Not competitors. FastAPI serves TCA's HTTP. Temporal is where a TCA operation runs when the process must survive the night. Hamilton and Dagster derive order from declarations for data, not applications.

Who should not use it: a service that is CRUD with few decisions; a team that wants a function when a type is in the way; rules that business users edit at runtime; a process that must itself survive a restart.
