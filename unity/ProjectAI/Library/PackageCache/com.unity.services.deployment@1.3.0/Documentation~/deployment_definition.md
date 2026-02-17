# Deployment Definition

﻿# Deployment Definitions

Deployment Definitions are analogous to assembly definitions,
but associated with deployable assets.

They allow you to group a set of deployable assets or code
into a logical grouping and associate settings with them.
You can use this grouping for easier deployment in the Deployment window.

By default, all assets are assigned to the `Default` Deployment Definition.

Each folder can have only one Deployment Definition. However, subfolders can also contain other Deployment Definitions.
All deployable assets inside a folder are assigned to the Deployment Definition in the folder.
If a sub-folder doesn't contain a Deployment Definition, any deployable assets are assigned to the Deployment Definition in the parent folder.

## Create Deployment Definitions

To create a Deployment Definition in a folder, right-click on the Project window, then select **Create** > **Deployment Defintion**.

## Modify Deployment Definitions

You can modify Deployment Definitions in the **Inspector**. To open the Deployment Definition in the **Inspector**, select the Deployment Definition in the **Project** window. You can also open it in your preferred IDE from the **Project** window (right-click > **Open**).

To locate a Deployment Definition in the **Project** window, right-click it in the [**Deployment window**](./deployment_window.md) and choose **Select in Project window** in the context menu.

## Exclude Paths

Deployment Definitions allows you to exclude certain files in your assets folder from deployment.

Exclude paths support 2 types of entries:

- Project relative paths (i.e. `Assets/DeployableAssets/MyDeployableAsset.ext`)
- Glob patterns (i.e. `**/Tests/**`)

Here is a detailed example of Exclude Paths in use

**Project Hierarchy**
```
Assets/
├── DeployableAssets/
│   ├── scriptA.js
│   ├── scriptB.js
│   ├── lib.js
│   └── Tests/
│       ├── ScriptA_tests.js
│       └── ScriptB_tests.js
```

**Deployment Definition**
```ddef
{
  "name": "Example",
  "excludePaths": [
    "Assets/BundleTest/lib.js",
    "**/Tests/**"
  ]
}
```

The result of this project hierarchy and Exclude Paths will result in only `scriptA` and `scriptB` being displayed in the Deployment window.

## Deploy Deployment Definitions

The [Deployment window](./deployment_window.md) displays Deployment Definitions and all their
associated assets.

To deploy a Deployment Definition select it and click **Deploy Selected**,
or right-click and select the **Deploy** context menu item.
