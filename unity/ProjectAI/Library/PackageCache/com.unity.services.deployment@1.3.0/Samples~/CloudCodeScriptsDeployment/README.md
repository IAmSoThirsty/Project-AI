# Cloud Code Scripts

This sample shows a simple way to deploy and invoke a Cloud Code Script.

## Using the Sample

### Setting up NodeJS

In order to have full support for your scripts in the editor, you need to set up NodeJS.
Navigate to `Preferences > Cloud Code` and make sure the path to NodeJS and NPM are correct.
Once set, click on the `Initialize JS Project` button.

### Deploying your Script

In order to deploy your script to the Cloud Code service, do the following:

1. Link your unity project in `Project Settings > Services`.
2. Select your desired environment in `Project Settings > Services > Environment`.
3. Initialize the JS project to allow for proper IDE setup and in-script parameters in `Preferences > Cloud Code > Initialize JS Project`.
4. Deploy your Cloud Code Script in the [Deployment window](https://docs.unity3d.com/Packages/com.unity.services.deployment@latest/manual/deployment_window.html).

### Play the Scene

To test out the sample, open the `CloudCodeScripts` scene in the Editor and click `Play`.
There is an input field where you can click and put text.
Clicking on the `Hello!` button in the Game window will call the cloud code script with the format `Hello {input_field_text}!`

You can modify your Cloud Code script and deploy while the scene is deploy to test the sample further.
Do note that the runtime invocation to call a script named `HelloScript`.

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

### Hello undefined

If you are receiving the `Hello undefined!` message, this is likely due to your JS project not being set up.
Refer to step `3` from [Deploying your Script](#deploying-your-script).
