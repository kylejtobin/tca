# TCA

## Positioning

For the developer who builds the backend services of a business, the ones with rules, external parties and decisions, TCA is a backend application framework whose runtime constructs business conclusions from typed dependencies and performs the external interactions those constructions require. The developer writes the service as types and nothing else. Every other framework on the shelf checks the edges of a service and hands the middle to a method the developer writes; TCA has no middle. There is no function between what arrives and what leaves, so the type checker reads the whole program and the program refuses what the business does not allow. It is built in Python, on Pydantic.

## The customer

One person: the developer who builds business services and has shipped a bug from a service method that passed the type checker and the tests. They learned the layered habit in Spring or ASP.NET, or in its Python copies. They choose their own tools, read alone, and judge by trying.

The same program serves five others, with nothing written for any of them:

- the developer on day one, with the business written and no server, who runs it from the shell and sees it answer;
- the operator who replays one request against staging without reading the code;
- the integrator who reads, in the API document, the descriptions the developer wrote on the fields;
- the reader who knows the business and not the code, who confirms the program says the business;
- the reasoning model that writes the service, judged by the same checker as a person.

## The problem

In the layered habit every layer has a tool that checks it except the one that matters. The framework validates what arrives. The database holds the schema. The container checks the wiring. The service, where every rule, every call and every decision lives, is checked by nothing but tests. The same model is written three times, with a mapper between each pair, and the documentation is a copy that drifts. Every framework on the shelf was built to host that service method well. None was built to remove it, because the method is where its applications live.

## The promise

Each of these is a commitment, and each could be proven false.

- A value the business does not have cannot exist in the program. A rule is a type, and the wrong value has no type.
- A rule that compares values, a value computed from others, and a choice among several are each declared, with their parts named, and the framework compares, computes and chooses. The program contains no expression.
- The type checker reads the whole program. There is no service, no handler and no function between what arrives and what leaves.
- A program that is wired wrong does not start. A question nothing answers, a value nothing produces, two things that each need the other, two outcomes that could both be true, or a rule its own bounds make certain or impossible is named, in the developer's own names, before anything runs.
- The developer says each thing once, and says only the business. Nothing in the program exists for the framework.
- Nothing is ordered. Each thing exists when what it is made of exists, and things that need nothing from each other happen together.
- A party is asked once per request, when what the question is made of exists. A question that must wait on an outcome is made of that outcome. Nothing else decides when a party is asked.
- The command line, the API and the documentation are one definition, read from the types. Choosing one or both changes nothing the developer wrote, and nothing drifts because nothing is a copy.
- There is one way to fail. A value outside the business is refused by name, the same way from the shell and from a request body. A party that does not answer raises its own client's error, and a request that cannot conclude names what it is missing. Nothing else fails, because nothing else runs.
- A party's refusal is an answer, not an exception, and it reaches the caller as a reply.
- Every request is a trace in the developer's words, one span per party asked, with no contents recorded.

## How it grows

The framework knows no business. The engine asks Pydantic for each class a program declares and keeps what constructs; it does not know what a discount, a quote or a screen is, and it never will. Everything a business does is a kind: a value computed from others, a comparison, a choice among several, a question to a party over one transport. A kind is written once, verified once, and belongs to every program from then on.

That sets how the product grows and how it is maintained. A new operation is a kind and changes no program and no engine. A new transport is a kind and changes no program. A new business is a program and teaches the engine nothing. A defect in an operation is fixed once, in its kind, for every program that declares it. The runtime stays small while what can be said in it grows, and the measure of a release is the kinds it adds, not the mechanisms.

## Why it cannot be copied

Every framework on the shelf has an authored middle, and that middle is where its applications live. A container resolves the dependencies of a service object and then hands control to its method. A typed effect system types every dependency and error and then runs the function the developer composed. An API written as a type checks every handler against it and then runs the handler. Each is a better way to host the code the developer writes between request and reply.

TCA's advantage is that there is no such code. That cannot be added to a framework as a feature, because a framework with no middle is not the same framework with something removed; its container, its lifecycle, its interfaces and its proof all exist to serve the construction of types, and the construction is the program. A team that adopts TCA's kinds inside Spring has a Spring service that calls them. The absence is the product.

## The scope

What it is: a backend application framework. It owns the configuration, the connections, the lifecycle, the wiring, the request boundary, the interfaces and the trace. It also owns the logic, because the logic is types.

What stays the developer's: Pydantic, the strict type checker, the HTTP server, the database, the trace exporter.

What it refuses to be: a validation framework, because validation is Pydantic's; a workflow engine, because there is no step, stage or plan; a DSL, because every construct is one Pydantic already documents; a handler framework, because there is no function between request and reply; a command-line framework, because each thing the program does is already the command.

There is no escape hatch inside a program. The only code that speaks to another system is the framework's, one kind per transport, and a program never contains it. Anything a program cannot express is a missing kind or a missing transport, and that is a defect in the framework.

What finishing takes: the HTTP boundary over the same request and reply types the shell already serves, and the kinds and transports the first production program needs. It does not take an ORM, a durability engine, a rules engine, a plugin ecosystem or a second application model. What remains is small because the engine is finished in shape, and the growth is in kinds.

## The principles

A program is nothing but a true description of a business, and it runs because it is true.

The measure of every decision: the developer says less, says it once, and says only their world. A design that makes the developer say more, or say anything for the framework, is wrong even when it works.

Why it is built this way. Types made the machine able to hold what the developer means, and every framework stopped them at the edges. TCA takes types through the middle, so the program is the statement of what exists in the business and what follows from what, and the statement is what runs. Because the program is a world that refuses what is false, a mind can be let into it, a person's or a model's, and its errors cannot run: a model writes a constrained set of declarations, the same checker and the same proof judge them, and there is no procedure left over to review. The wrong program cannot be written. The business is the program. Judgment can be put in production.

The defect rules. Anything in a program that exists for the framework is a defect in the framework. Any behavior in the framework that the developer should have declared is a defect in the framework. Any failed observation below is a defect in the framework, never in the program.

## The evidence

The promise is kept when each of these is observed on any program written against the framework.

- Every function in a program is a property of a type that reads its fields; none computes.
- The strict type checker reports nothing.
- Removing the one thing that receives a party's answer stops the program at startup, naming that answer.
- The parties a request asks are exactly those its reply is made of, each asked once.
- A developer who has read Pydantic's documentation and one program writes the next operation without opening the framework.
- A reader who knows the business names what each type is from its name and description.
- A new operation is one kind, and every existing program can declare it without a change.
- The framework has no public types of its own, and one entry per interface.
- The program's help lists every operation, every field with its description, and every variable the deployment sets, from the program alone.
- The same request answered from the shell and over HTTP gives the same body.
- An operator replays a request against an environment without reading code.
- The served API document and the shell's help show the same fields and the same descriptions.
- A value outside a rule is refused the same way from the shell and from a request body, naming the field and nothing else.

## The category and the competitors

The shelf is backend application frameworks. The comparison that matters is not what each provides but what each leaves the developer to write.

| Framework | What the developer still writes |
| --- | --- |
| Spring Boot | the service methods the container hands control to |
| ASP.NET Core | the application methods behind the middleware and the injection |
| NestJS | the provider methods behind the modules and controllers |
| Django, Rails | the application behavior behind the models and conventions |
| Effect, ZIO | the effectful program that composes the typed dependencies and errors |
| Servant | the handlers the API type checks |
| TCA | declarations, composed from kinds |

The strongest are the ones that can nearly say the middle is checked. Effect and ZIO type every dependency and error and resolve them at compile time, and then run the function the developer wrote. ASP.NET Core with F# has the strongest checker on the shelf and a community that already models a business as states that cannot be wrong, with the ideology and the framework in separate hands. Spring Boot's container resolving a graph of types is TCA's startup proof and its run, up to the service object, where it stops. Servant defines the API once as a type and derives everything from it, which is half the promise; the other half, no handler at all, is where it stops.

Not competitors. FastAPI serves TCA's HTTP. Temporal is where a TCA operation runs when the process must survive the night. Hamilton and Dagster derive order from declarations for data, not applications.

Who should not use it: a service that is CRUD with few decisions; a team that wants a function when a type is in the way; rules that business users edit at runtime; a process that must itself survive a restart.
