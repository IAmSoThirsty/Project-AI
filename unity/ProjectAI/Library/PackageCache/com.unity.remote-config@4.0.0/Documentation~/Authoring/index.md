# Remote Config Authoring

This module allows users to author, modify, and deploy Remote Config files directly from the Unity Editor.

> NOTE: Remote Config Authoring is only supported on Unity 2021.3 and above.

### Deployment Window

The Deployment Window is a core feature of the Deployment package.

The purpose of the Deployment Window is to allow all services
to have a single cohesive interface for Deployment needs.

The Deployment Window provides a uniform deployment interface for all services.
It allows you to upload cloud assets for your respective cloud service.

For more information, consult the [com.unity.services.deployment](https://docs.unity3d.com/Packages/com.unity.services.deployment@latest) package documentation.

### Create Remote Config files

Right-click the Project Window, then select `Assets > Create > Remote Config` to create a Remote Config file.

The Deployment Window automatically detects these files to be deployed at a later time.

For more information on how to create and modify Cloud Code Assets,
please see the [Remote Config file](./remote_config_files.md) documentation.
