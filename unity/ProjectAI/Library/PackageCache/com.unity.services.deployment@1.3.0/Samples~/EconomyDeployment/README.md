# Economy

This sample shows a simple way to deploy and use an Economy item.

## Using the Sample

### Deploying your Economy item

In order to deploy your economy item to the Economy service, do the following:

1. Link your unity project in `Project Settings > Services`.
2. Select your desired environment in `Project Settings > Services > Environment`.
3. Deploy `MYCURRENCY.ecc` in the [Deployment window](https://docs.unity3d.com/Packages/com.unity.services.deployment@latest/manual/deployment_window.html).

### Play the Scene

To test out the sample, open the `Economy` scene in the Editor and click `Play`.

You should see 3 buttons on screen:

1. display currency details
2. increase balance
3. reset balance

Clicking on `display currency details` will refresh the cached currency data from the Economy service and display details in the log.

Clicking on `increase balance` will increase the current player balance and display the new value in the console.
If the max balance is reached, you will see errors in the console, suggesting to click on the `reset balance button`.

Clicking on `reset balance` will set the current balance back to the initial value.

> **_NOTE:_**  It can be interesting to modify the economy file and redeploy it during playmode. You can then click
> `display currency details` and notice it has been updated.

## Package Dependencies

This sample has dependencies to other packages.
If your project does not have these packages, they will be installed.
If your project has the packages installed but they are of a previous version, they will be updated.
A log message indicating which package is installed at which version will be displayed in the console.

The following packages are required for this sample:

- `com.unity.services.authentication@3.2.0`
- `com.unity.services.economy@3.3.1`

## Troubleshooting

### Empty Deployment window

If the deployment window is empty, make sure your project is linked in `Project Settings > Services` and that you have selected an environment in `Project Settings > Services > Environments`.
