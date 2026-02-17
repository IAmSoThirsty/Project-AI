# Getting started

This page describes how to get started with the Deployment package, and some common use cases.

* [Project setup](#project-setup)
* [Access the Deployment window](#access-the-deployment-window)
* [Create deployable assets](#create-deployable-assets)
* [Select assets](#select-assets)
* [Deploy assets](#deploy-assets)
* [Group assets](#group-assets)


<a name="project-setup"></a>

## Project setup

Before using the deployment package make sure that your project is properly set up.

1. Install the Deployment package (com.unity.services.deployment) using the Unity Package Manager. Learn more about [adding and removing](https://docs.unity3d.com/Manual/upm-ui-actions.html) packages.
1. In the Unity Editor toolbar go to:
    -  on `2021.3+`: **Edit** > **Project Settings** > **Services**
    -  on `2022+`: **Services** > **General Settings** > **Services**
1. Create a Unity Project ID or link to an existing one.
1. Switch to **Services** > **Deployment** tab and select the [environment](./environments.md) you want to work in.
1. Install a [supported package](./index.md#supported-packages). This is required to be able to create deployable assets.

<a name="access-the-deployment-window"></a>

## Access the Deployment window

To open the [Deployment window](./deployment_window.md), in the Editor toolbar go to:

- on `2021.3+`: **Window** > **Deployment**
- on `2022+`: **Services** > **Deployment**

<a name="create-deployable-assets"></a>

## Create deployable assets

The Deployment package doesn't provide the ability to create deployable assets. For this, refer to the documentation of the supported package you intend to use.

<a name="select-assets"></a>

## Select assets

To select assets in the [Deployment window](./deployment_window.md), you can:

* Select the checkbox of an asset.
* Select the checkbox of a deployment definition to select all assets under that deployment definition.

<a name="deploy-assets"></a>

## Deploy assets

When you have installed a supported package and created a deployable asset, the Deployment window displays your deployable assets.

You can deploy assets:

* Manually in the Deployment window
* Automatically on Play

### Deploy assets in the Deployment window

You can deploy assets manually in the Deployment window in the following ways:

* Double-click an asset.
* Right-click an asset and select **Deploy**.
* Select **Deploy All**.
* Select assets and select **Deploy Selected**.

> [!NOTE]
> When you deploy a Deployment Definition, all of its assets are deployed.

### Deploy assets automatically on Play

To deploy assets automatically on Play:

1. In the Deployment window, select the assets to deploy automatically.
1. Select the **More** (&#8942;) menu.
1. Ensure the **Deploy Selected On Play** is toggled on.

Now, when you enter Play Mode in the Editor, the selected assets are deployed.

<a name="group-assets"></a>

## Group assets

To group assets you need to use a [Deployment Definition](./deployment_definition.md). If no deployment definition is present, everything is grouped under a single `Default` deployment definition.
