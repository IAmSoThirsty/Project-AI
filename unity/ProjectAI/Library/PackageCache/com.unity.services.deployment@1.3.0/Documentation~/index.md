# Deployment package

The Deployment package provides a cohesive interface to deploy assets for Unity Gaming Services (UGS).
It provides the base tooling for UGS to have shared functionality for deploying service configuration files on the servers.

> [!NOTE]
> A deployment is when service configuration files are synced
with service resources so that service clients can interact with them.

The Deployment package is not used on its own. Services integrate with it, allowing the service configuration to
be saved in version control.

|Topic|Description|
|---|---|
|[Getting started](./getting_started.md)|Get started with the Deployment package.|
|[Deployment window](./deployment_window.md)|Use the Deployment window to deploy assets.|
|[Deployment Definition](./deployment_definition.md)|Use Deployment Definitions to group assets for deployment.|
|[Environments](./environments.md)|Deploy assets to specific environments.|

## Supported packages

- [com.unity.services.cloudcode (javascript)](https://docs.unity.com/ugs/en-us/manual/cloud-code/manual/scripts/how-to-guides/write-scripts/unity-editor) **from 2.1.0**
- [com.unity.services.cloudcode (C#)](https://docs.unity.com/ugs/en-us/manual/cloud-code/manual/modules/how-to-guides/write-modules/unity-editor) **from 2.5.0**
- [com.unity.remote-config](https://docs.unity.com/ugs/en-us/manual/remote-config/manual/remote-config-files) **from 3.2.0**
- [com.unity.services.economy](https://docs.unity.com/ugs/en-us/manual/economy/manual/deploying-resources-with-unity-editor) **from 3.2.1**
- [com.unity.services.leaderboards](https://docs.unity.com/ugs/en-us/manual/leaderboards/manual/leaderboards) **from 2.0.0**
- [com.unity.services.multiplay](https://docs.unity.com/ugs/en-us/manual/game-server-hosting/manual/welcome) **from 1.1.0**
