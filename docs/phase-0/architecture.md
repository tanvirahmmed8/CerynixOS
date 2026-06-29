# Device-Plane Architecture

```mermaid
flowchart TD
    %% Base OS Layer
    subgraph Base [Immutable Base (NixOS)]
        Kernel[Linux Kernel / eBPF]
        Config[Declarative State]
        Rollback[Rollback Engine]
    end

    %% Observability & Health
    subgraph Obs [Observability & Health]
        Telemetry[Telemetry Agent]
        Health[Health Agent]
        Drift[Drift Detector]
    end

    %% AI & Automation
    subgraph AI [AI & Automation]
        Runtime[Local AI Runtime]
        Optimizer[Optimization Engine]
        Memory[Task Memory]
    end

    %% Execution & Security
    subgraph Exec [Execution & Security]
        Broker[Action Broker]
        Audit[Audit Logger]
        Policy[Policy Agent]
        Plugins[Plugin Runtime]
    end

    %% User Experience
    subgraph UX [User Experience]
        Shell[Desktop Shell]
        Assistant[AI Assistant UI]
        Dash[Optimization Dashboard]
    end

    %% Update & Recovery
    subgraph Updates [Update & Recovery]
        UpdateAgent[Update Agent]
    end

    %% Relationships
    Kernel --> Telemetry
    Telemetry --> Optimizer
    Telemetry --> Health
    Config --> Drift
    Drift --> Rollback
    UpdateAgent --> Rollback
    UpdateAgent --> Config

    Assistant --> Runtime
    Runtime --> Memory
    Runtime --> Broker
    Plugins --> Broker

    Broker --> Policy
    Broker --> Audit
    Broker --> Kernel
    Broker --> Config

    Policy -.-> |Reads| MockPolicy[(Mock Remote Policy)]
    UpdateAgent -.-> |Reads| MockUpdate[(Mock Update Metadata)]
    Health -.-> |Writes| MockHealth[(Mock Remote Backend)]
```

## Key Architectural Decisions
1. **Action Broker as the Choke Point:** The AI Runtime cannot modify the system directly. It must request tools via the Action Broker, which evaluates the action against the active policy.
2. **Declarative State for Safety:** System-level changes made by the Updater, Healer, or AI Broker are applied by generating new Nix configurations and activating them, ensuring instant revertability.
3. **Mocks for the Control Plane:** The Update, Policy, and Health agents communicate with local JSON file fixtures to simulate interactions with the future enterprise control plane.
