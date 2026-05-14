# Admin Service Deployment

Task: T-1103b

The admin-service is the only process that hosts administrator write paths:
authorisation profile writes, SOP-template admin writes, audit-key rotation, and
review-queue resolution. CLI, API, and engine processes use
`AdminServiceClientPort` and never import `AdminActionHandler` directly.

## IPC Endpoints

- Windows named pipe: `\\.\pipe\cev-admin-service`
- POSIX Unix socket: `/var/run/cev-admin/socket`

Frames use the T-1103a length-prefixed JSON contract documented in
`docs/admin_service/ipc_contract.md`.

## Windows Service

Run the service under a dedicated account such as `cev-admin-svc`. The named
pipe ACL must allow only:

- local Administrators group SID `S-1-5-32-544`
- the admin-service account SID

The engine service should run under a separate account such as `cev-engine-svc`.
Manual verification:

```powershell
vector-design-admin-service
```

Confirm the configured pipe path and service account, then validate the pipe
security descriptor with the Windows service tooling used by the deployment.

## POSIX Service

Run the service under `cev-admin-svc` and group `cev-admin`. The socket file
must be owned by the admin-service account/group and use mode `0660`.

Example systemd unit shape:

```ini
[Service]
User=cev-admin-svc
Group=cev-admin
ExecStart=/opt/cev/bin/vector-design-admin-service
RuntimeDirectory=cev-admin
RuntimeDirectoryMode=0750
```

The engine process should run under a distinct account, for example
`cev-engine-svc`, and should not be a member of `cev-admin` unless explicitly
authorised for admin IPC.
