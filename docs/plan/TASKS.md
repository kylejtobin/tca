# Tasks

## Todo

- [ ] T04 | Application declaration | Expose the minimal `Application` declaration and installed launch entry. Applications identify their configuration through models. Resource composition selects the supplied execution integration without a second backend setting; importing declarations performs no configuration loading or connection startup. | outcome:O01
- [ ] T05 | Shared native startup | Realize declared resources through the selected integration's bindings and FastStream's common lifecycle facilities. Verify empty startup, invalid configuration before connection, cleanup after partial initialization failure, and shutdown. | outcome:O01
- [ ] T06 | Container startup integration | Connect the shared launch entry to the existing Docker, Compose, just, and CI setup. Verify the built, installed framework starts a minimal declared application in the TCA container and connects to secured, persistent JetStream-enabled NATS. | outcome:O01
- [ ] T07 | Typed event contract | Implement `Event` through native Pydantic construction and serialization, preserving typed content, occurrence identity, source context, and actual input basis. Preserve integration-specific retained evidence identity without universal NATS stream/sequence fields. | outcome:O03
- [ ] T08 | NATS topology binding | Implement the NATS topology binding from declared placements and relationships. Derive subjects and stable stream/consumer identities across workers; configure shared durable pull consumers and file-backed `LimitsPolicy` history with deployment-supplied replication and placement. Repeated roles remain distinct; ordinary business fields create no messaging resources. | outcome:O03
- [ ] T09 | Event source binding | Connect shared `Source` semantics through the selected integration's native FastStream receiving and admission bindings. Preserve source and occurrence context, including agreement between addressed context and received content. | outcome:O03
- [ ] T10 | Activity execution binding | Connect shared `Activity` semantics through the selected integration's native bindings to the selected Pydantic construction or supported operation and declared result destinations. Acknowledge only after confirmed retained publication. Verify successful A-to-B delivery and construction/publication failures through an installed application containing no handwritten handlers or transport wiring. | outcome:O03

## Doing

- [ ] T03 | Broker resource | Separate the general resource contract from its NATS specialization and native binding. Preserve runtime-scoped ownership, shared use, and native access; keep provider dependencies and exports within the integration boundary. Establish secure connections and verify the combined dependency, configuration, and resource foundation. | outcome:O01 | agent:claude
