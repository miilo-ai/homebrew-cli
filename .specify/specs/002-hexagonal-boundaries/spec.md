# Architecture boundary enforcement

Domain/application owns ports and policy; infrastructure implements those ports.
Executable/runtime composition chooses concrete implementations. Core use cases
must run with fake ports. Compatibility entry points remain explicit at the edge.
The constitution and architecture policy describe the enforced source scope.

The repository remains packaging-only. Architecture CI rejects application source/crates/packages here. No observation logic or runtime was added.
