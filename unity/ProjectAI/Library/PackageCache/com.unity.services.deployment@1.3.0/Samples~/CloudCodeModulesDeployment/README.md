# Cloud Code Modules

This sample shows a simple way to deploy and invoke a cloud code module.

## Using the Sample

### Deploying your Module

In order to deploy your module to the Cloud Code service, do the following:

1. Link your unity project in `Project Settings > Services`.
2. Select your desired environment in `Project Settings > Services > Environment`.
3. Deploy your Cloud Code Module (`HelloSample.ccmr`) in the [Deployment window](https://docs.unity3d.com/Packages/com.unity.services.deployment@latest/manual/deployment_window.html).

### Play the Scene

To test out the sample, open the `CloudCodeModules` scene in the Editor and click `Play`.
You can click the input field in the Game window and input some text
Clicking on the `Hello!` button in the Game window will call the Cloud Code Module and output a message with the format `Hello [input_text_here]!`.

This sample's Cloud Code module is located at `Assets/Samples/Deployment/{version}/Cloud Code Modules Deployment/SampleContent/Module~`.
Note that it is invisible in the editor project window but is visible in your file browser.

You can modify your Cloud Code module while the scene is playing and deploy it again to test out the sample further.

Do note that the script invoking the method at runtime expects to pass a string parameter with the name `name` to a method with the `[CloudCodeFunction("SayHello")]` attribute on it.

## Package Dependencies

This sample has dependencies to other packages.
If your project does not have these packages, they will be installed.
If your project has the packages installed but they are of a previous version, they will be updated.
A log message indicating which package is installed at which version will be displayed in the console.

The following packages are required for this sample:

- `com.unity.services.authentication@3.2.0`
- `com.unity.services.cloudcode@2.5.2`

## Troubleshooting

### Empty Deployment window

If the deployment window is empty, make sure your project is linked in `Project Settings > Services` and that you have selected an environment in `Project Settings > Services > Environments`.
