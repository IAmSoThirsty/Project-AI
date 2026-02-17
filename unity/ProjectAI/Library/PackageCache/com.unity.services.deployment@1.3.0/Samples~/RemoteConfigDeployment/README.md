# Remote Config

This sample shows a simple way to deploy and use a Remote Config.
The Remote Config service allows you to store some of your game configuration remotely,
which allows you to re-configure your game without deploying new game binaries.

## Using the Sample

### Deploying your Remote Config

To deploy your config to the Remote Config service, do the following:

1. Link your unity project in `Project Settings > Services`.
2. Select your desired environment in `Project Settings > Services > Environment`.
3. Deploy `sample-remote-config.rc` in the [Deployment window](https://docs.unity3d.com/Packages/com.unity.services.deployment@1.2/manual/deployment_window.html).

### Play the Scene

To test out the sample, open the `RemoteConfig` scene in the Editor and click `Play`.

You should see 2 columns on the screen:

1. display remote config keys
2. display remote config values

You should see a button on the screen:

1. get config

Clicking on `Get Config` will refresh the cached config data from the Remote Config service and display details on the screen.

> **_NOTE:_**  It can be interesting to modify the remote config file and redeploy it during play mode. You can then click
> `Get Config` and notice it has been updated.

## Package Dependencies

This sample has dependencies to other packages.
If your project does not have these packages, they will be installed.
If your project has the packages installed but they are of a previous version, they will be updated.
A log message indicating which package is installed at which version will be displayed in the console.

The following packages are required for this sample:

- `com.unity.services.authentication@3.2.0`
- `com.unity.remote-config@4.0.0`

## Troubleshooting

### Empty Deployment window

If the deployment window is empty, make sure your project is linked in `Project Settings > Services` and that you have selected an environment in `Project Settings > Services > Environments`.
