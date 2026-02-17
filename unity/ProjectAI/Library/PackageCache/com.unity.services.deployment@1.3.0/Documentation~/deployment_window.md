# Deployment window

The Deployment window lets you deploy assets to their respective services, as well as other relevant
service-specific manipulations. The Deployment window detects and displays any deployable assets in your project.

To access the Deployment window:

* In 2021 or before, use **Window** > **Deployment**.
* In 2022 and later, use **Services** > **Deployment**.

## Deployment window UI

The following table describes the Deployent window.

<table>
  <thead>
    <tr>
      <th colspan="1"><strong>Field</strong></th>
      <th colspan="2"><strong>Description</strong></th>
    </tr>
  </thead>
  <tbody>
    <tr>
        <td><strong>Deploy Selected</strong></td>
        <td colspan="2">Deploys the selected assets to the chosen environment.</td>
    </tr>
    <tr>
        <td><strong>Deploy All</strong></td>
        <td colspan="2">Deploys all assets to the chosen environment.</td>
    </tr>
    <tr>
        <td>Environment view</td>
        <td colspan="2">Shows the current environment where the assets will be deployed to. &lt;br/&gt;This dropdown contains a shortcut to <strong>Project Settings</strong> &gt; <strong>Services</strong> &gt; <strong>Deployment</strong> &gt; <strong>Environment Selector</strong> where you can modify the environment.</td>
    </tr>
    <tr>
        <td rowspan="3"><strong>More</strong> (&vellip;) menu</td>
        <td colspan="2">Contains additional options for the Deployment window.</td>
    </tr>
    <tr>
        <td><strong>Deploy All on Play</strong></td>
        <td>Triggers all assets to be deployed when the Unity Editor transitions from edit mode to play mode. The Unity Editor waits for file deployment to be completed before entering play mode.</td>
    </tr>
    <tr>
        <td><strong>Block Playmode on Failure</strong></td>
        <td>Blocks Play Mode from running when a file fails to deploy via <strong>Deploy Selected on Play</strong>.</td>
    </tr>
    <tr>
        <td><strong>Name</strong></td>
        <td colspan="2">Displays the name of the asset.</td>
    </tr>
    <tr>
        <td><strong>Service</strong></td>
        <td colspan="2">Displays the name of the service that the asset relates to.</td>
    </tr>
    <tr>
        <td><strong>Deployment Status</strong></td>
        <td colspan="2">Describes the status of an asset with respect to the remote resource.</td>
    </tr>
    <tr>
        <td>Status panel</td>
        <td colspan="2">The status panel in the bottom of the Deployment window describes additional details regarding an asset's status. An asset can contain multiple states.</td>
    </tr>
    <tr>
        <td rowspan="4">Context menu</td>
        <td colspan="2">Displays additional actions available for each asset, depending on the service. Right-click on an asset to display the context menu.</td>
    </tr>
    <tr>
        <td><strong>Deploy</strong></td>
        <td>Deploys the selected items.</td>
    </tr>
    <tr>
        <td><strong>Select In Project Window</strong></td>
        <td>Selects the asset in the Project window if it is an Unity asset.</td>
    </tr>
    <tr>
        <td><strong>Open</strong></td>
        <td>Opens the asset in the appropriate editor, for supported assets.</td>
    </tr>
  </tbody>
</table>

## Icons

### Warning

The warning icon is displayed to highlight an issue with the asset.

### Error

The error icon is displayed when the asset has failed to deploy or there are other failure states associated with each service.
