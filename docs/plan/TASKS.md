# Tasks

## Todo

- [ ] T04 | Application declaration | Expose the minimal `Application` declaration and installed launch entry. Applications identify their configuration through models; importing declarations performs no configuration loading or connection startup. | outcome:O01
- [ ] T05 | Shared native startup | Realize declared resources through their native bindings and invoke FastStream lifecycle management. Verify empty startup, invalid configuration before connection, cleanup after partial initialization failure, and shutdown. | outcome:O01
- [ ] T06 | Container startup integration | Connect the shared launch entry to the existing Docker, Compose, just, and CI setup. Verify the built, installed framework starts a minimal declared application in the TCA container and connects to persistent JetStream-enabled NATS. | outcome:O01
- [ ] T07 | Typed event contract | Implement `Event` through native Pydantic construction and serialization, preserving typed content, occurrence identity, source context, and the actual input basis accompanying produced results. | outcome:O03
- [ ] T08 | Native topology binding | Derive subjects and stable stream/consumer identities across workers from declared placements and relationships. Configure shared durable pull consumers and file-backed `LimitsPolicy` history through native facilities, applying deployment-supplied replication and placement settings. Repeated roles remain distinct; ordinary business fields create no messaging resources. | outcome:O03
- [ ] T09 | Event source binding | Connect `Source` declarations to native FastStream typed receiving and the declared admission contract. Preserve source and occurrence context, including agreement between addressed context and received content. | outcome:O03
- [ ] T10 | Activity execution binding | Connect `Activity` declarations to framework-owned functions that invoke the selected Pydantic construction or supported operation and publish typed results to their declared destinations. Use native acknowledgement after confirmed retained publication. Verify successful A-to-B delivery and construction/publication failures through an installed application containing no handwritten handlers or transport wiring. | outcome:O03

## Doing

- [ ] T03 | Broker resource | Implement `Resource` for the native NATS broker’s configuration, runtime-scoped ownership, and shared use. Preserve native broker/client access and delegate lifetime operations to FastStream. | outcome:O01 | agent:claude
