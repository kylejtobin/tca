# Tasks

## Todo

- [ ] T04 | Application declaration | Expose the minimal `Application` declaration and installed launch entry. Applications identify their configuration through models; importing declarations performs no configuration loading or connection startup. | outcome:O01
- [ ] T05 | Shared native startup | Construct native `NatsBroker` and FastStream objects from declared configuration and invoke native lifecycle management. Verify empty startup, invalid configuration before connection, cleanup after initialization failure, and shutdown. | outcome:O01
- [ ] T06 | Container startup integration | Connect the shared launch entry to the existing Docker, Compose, just, and CI setup. Verify the built, installed framework starts a minimal declared application in the TCA container and connects to persistent JetStream-enabled NATS. | outcome:O01
- [ ] T07 | Typed event contract | Implement `Event` through native Pydantic construction and serialization, preserving typed content, occurrence identity, source context, and the actual input basis accompanying produced results. | outcome:O03
- [ ] T08 | Native topology binding | Derive subjects and required stream/consumer names from declared placements and relationships. Configure native `JStream` and `ConsumerConfig` objects; repeated roles remain distinct, and ordinary business fields create no messaging resources. | outcome:O03
- [ ] T09 | Event source binding | Connect `Source` declarations to native FastStream typed receiving and the declared admission contract. Preserve source and occurrence context, including agreement between addressed context and received content. | outcome:O03
- [ ] T10 | Activity execution binding | Connect `Activity` declarations to framework-owned functions that invoke the selected Pydantic construction or supported operation and publish typed results to their declared destinations. Use native acknowledgement after confirmed retained publication. Verify successful A-to-B delivery and construction/publication failures through an installed application containing no handwritten handlers or transport wiring. | outcome:O03

## Doing

- [ ] T03 | Broker resource | Implement `Resource` for the native NATS broker’s configuration, application ownership, and shared use. Keep the live client native and delegate its lifetime to FastStream. | outcome:O01 | agent:claude
