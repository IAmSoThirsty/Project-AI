# Changelog

All notable changes to this package will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

## [16.3.0] - 2024-04-17

### Added

 - `VivoxConfigurationOptions.BluetoothProfile` for configuring the type of Bluetooth profile Vivox should use. This configuration currently affects only mobile devices.
 - `VivoxConfigurationOptions.MobileRecordingConflictAvoidance` property to enable/disable mobile recording conflict avoidance.This configuration currently affects only Android mobile devices.
 - `IVivoxService.EffectiveInputDeviceChanged` event to listen for when the effective input device changes.
 - `IVivoxService.EffectiveOutputDeviceChanged` event to listen for when the effective output device changes.
 - `IVivoxService.EffectiveInputDevice` property to provide information about the current effective input device.
 - `IVivoxService.EffectiveOutputDevice` property to provide information about the current effective output device.

 ### Changed

 - Upgraded `com.unity.services.core` dependency to version `1.12.5`.
 - Upgraded underlying Vivox Core SDK to version `5.23.1`.

### Fixed

 - Fixed a bug preventing the SDK from properly using UAS with particular Vivox backend environments.

## [16.2.0] - 2024-03-19

### Added

 - Support for Windows ARM64.
 - `VivoxMessage.RecipientPlayerId` property to provide the recipient's player ID to `VivoxMessage` objects returned from a `IVivoxService.GetDirectTextMessageHistoryAsync` query.
 - `VivoxMessage.IsTranscribedMessage` property to easily identify if a message is a speech-to-text transcribed message.
 - `IVivoxService.SpeechToTextEnableTranscription` method that allows you to enable the speech-to-text audio transcription inside a channel.
 - `IVivoxService.SpeechToTextDisableTranscription` method that allows you disable the speech-to-text audio transcription inside a channel.
 - `IVivoxService.IsSpeechToTextEnabled` method that allows you to check if the transcription is enabled or disabled inside a channel.
 - `IVivoxService.StartAudioInjection` method to allow you to start audio injection in a channel. Injected audio is played only into the channels you're transmitting into.
 - `IVivoxService.StopAudioInjection` method to allow you to stop audio injection in a channel.
 - `IVivoxService.IsInjectingAudio` method to allow you to know if audio is being injected.
 - `IVivoxService.SpeechToTextMessageReceived` Bind/Unbind this event handler to a method to get notified when a transcribed message is added.
 - `LoginOptions.SpeechToTextLanguages` A list of languages used as hints for audio transcription. The default is an empty array, which implies "en".

### Fixed

 - Fixed an issue with display names not being provided to new `VivoxMessage` objects when a user had supplied a display name while signing into Vivox.
 - Fixed a race condition that could prevent direct message or channel message history queries from being completed.
 - Fixed an issue where supplying a Player ID to the `IVivoxService.GetDirectTextMessageHistoryAsync` query would not correctly filter the results to that Player ID.
 - Fixed an issue where if either the text or audio plane of a channel failed to connect, or was unexpectedly disconnected, an error was not thrown and information about what occured was not provided.
 - Fixed an issue that would arise when leaving and immediately rejoining a channel resulting in an exception being thrown due to not being completely disconnected from the channel yet.
 - Fixed a Unity editor crash when calling Vivox APIs while exiting Play Mode.
 - Fixed a bug where a participant would have a low volume when leaving and rejoining a channel.
 - Fixed a bug where a participant transmitting to both a positional (3D) and a non-positional (2D) could only be heard in the non-positional channel.
 - Fixed a bug with Participant Audio Taps would only get audio in the first channel joined.
 - Fixed a build issue that would break TestFlight certification on iOS builds.
 - Fixed an issue where capture sounds would be robotic on some macOS devices.

## [16.0.1] - 2023-12-12

### Added

 - `IVivoxService.GetConversationsAsync` method for querying channel and direct message conversations a user has participated in.
 - `IVivoxService.SetMessageAsReadAsync` method for setting a message as seen/read.
 - `VivoxConversation` class to neatly encompass all of the details of a particular channel or direct message conversation.
 - `ConversationType` enum to help identify the type of conversation that is provided by `IVivoxService.GetConversationsAsync`.
 - `ConversationQueryOptions` class used to provide optional configurations for the `IVivoxService.GetConversationsAsync` query.

### Fixed

 - Fixed an issue where the default token expiration provided to `IVivoxTokenProvider.GetTokenAsync` was incorrect.
 - Fixed an issue causing an exception when calling `IVivoxService.LogoutAsync` while not in any channels.
 - Fixed an issue where the `IVivoxService.LogoutAsync` or `IVivoxService.JoinChannelAsync` methods would not complete if the user was not logged in.

### Removed

 - Removed `AudioFadeDistance.None` option as it is not a valid 3d option

## [16.0.0-pre.1] - 2023-09-14

### Added

 - Launch of the new Unity SDK with an easier-to-use API.
 - Vivox Unity SDK v16 is a major update to the API which will require manual changes. Follow the [16.0.0 upgrade guide](https://docs.unity.com/ugs/en-us/manual/vivox-unity/manual/Unity/v16-upgrade-guide) to upgrade an existing Unity Vivox implementation to this new version.
 - Audio Source per participant feature has been added.
 - Audio Source per channel feature has been added.
 - New Text Chat capabilities, featuring the addition of APIs for querying chat history and enabling the editing or deletion of sent direct or channel messages.

### Fixed

 - Fixed issues where users could hear repeated audio blips in the Core SDK.
 - Fixed an issue that triggered when joining a 3D channel after a 2D channel where session groups ignored clamping distance.
 - Fixed a crash that triggered when a user attempted to send a message while Automatic Connection Recovery was ongoing.

### Changed

 - Messages from blocked participants from chat history queries are now omitted.
 - Upgrading minimum Unity version support to 2020.3.

### Removed

- Substantial API revamp has resulted in the removal of the prior public API.

## [15.1.210000-pre.1] - 2023-08-01

### Changed

 - Upgrades underlying Vivox SDK Dependency to version 5.21.0

## [15.1.200100-pre.1] - 2023-05-08

### Changed

 - Upgrades underlying Vivox SDK Dependency to version 5.20.1

## [15.1.200000-pre.1] - 2023-03-15

### Changed

 - Upgrades underlying Vivox SDK Dependency to version 5.20.0
 - Obsoletion of the defunct SessionArchive and AccountArchive APIs

## [15.1.190400-pre.1] - 2023-01-06

### Changed

 - Upgrades underlying Vivox SDK Dependency to version 5.19.4

## [15.1.190200-pre.2] - 2022-12-21

### Fixed

 - Fixed an issue with the Android VivoxNative.aar library causing it to have issues when trying to resolve internal dependencies.

## [15.1.190200-pre.1] - 2022-09-26

### Changed

 - Upgraded underlying Vivox SDK dependency to version 5.19.2.

### Fixed

 - Fixed an issue with audio buffer-related generated APIs causing the Unity editor to crash.

## [15.1.190000-pre.1] - 2022-09-26

### Changed

 - Upgraded underlying Vivox SDK dependency to version 5.19.0.

## [15.1.180001-pre.5] - 2022-09-01

### Added

 - Added a number of generated APIs back to the SDK which were previously being omitted.

### Fixed

 - Fixed an issue with Build Configuration values being stored as nulls instead of empty strings which caused an exception in the editor if a project was not linked in the Project Settings.

## [15.1.180001-pre.4] - 2022-08-08

### Changed

 - Adjusted the Windows and Mac VivoxNative library .meta files to enable `Load on Startup` so they get loaded in regardless of the build target of the editor. Notably, this caused compiler errors when entering Play Mode if the editor build target was iOS since our Mac library, which gets used for the editor alongside the Windows library, wasn't loaded yet.

### Fixed

 - Fixed an issue with various plugin `.meta` files not targeting their specific platform resulting in editor crashes when entering Play Mode if additional Vivox platform packages got installed.
 - Fixed an issue that would cause a compiler error if the Authentication package wasn't available to the ChatChannelSample. The Authentication package should get automatically pulled in when the ChatChannelSample is installed, but if it hadn't been, a compiler error would appear.

## [15.1.180001-pre.3] - 2022-07-13

### Added

 - Added VivoxConfig as a parameter to the VivoxService.Instance.Initialize(...) method so developers can configure the Vivox Client's settings on startup.

### Changed

 - Stopped removing minus ('-') characters from the Environment ID when appending it to the AccountId and ChannelId URIs. The Environment ID will now be appended verbatim.

### Fixed

 - Fixed an issue causing generated files from the Android platform to make it into the package resulting in methods that could not be resolved due to the APIs not existing in any other library.

## [15.1.180001-pre.2] - 2022-06-22

### Fixed

- Fixed a warning that would always throw when using custom credentials via InitializationOptions.SetVivoxCredentials and initializing the Vivox service.
- Fixed IEnvironmentId not being added as an optional dependency in VivoxPackageInitializer.cs causing erroneous and confusing warnings when initializing the Vivox service.

## [15.1.180001-pre.1] - 2022-06-03

### Fixed

- Fixed how we fetch the Authentication package's Environment ID to fix the Vivox package not working when using newer versions of Authentication.
- Fixed debug/local token generation when Test Mode is enabled in the Vivox service settings and the user is signed into Authentication.

## [15.1.180000-pre.1] - 2022-05-02

### Added

- Automatic Connection Recovery has been added to the Unity API, along with an example Connection Indicator added to the Chat Channel Sample.

### Changed

- Fixed a bug that left the suggestion to add the Authentication package for easy Vivox Logins even after the Authentication package had been imported.

## [15.1.170000-pre.1] - 2022-02-25

### Added

- Added a display name to constructs provided by the SDK when events fire for receiving a message, a transcribed message, or a buddy request.

### Changed

- Removed the option to provide custom credentials in the Vivox service window.
- Updated ChatChannelSample to demonstrate how to leverage both Authentication and a custom credential-based flow.

## [15.1.160000-pre.1] - 2021-10-20

### Fixed

- Fixed a bug that prevented users from switching to the custom credentials option in the Vivox service window when Unity Game Services was enabled.
- Improved the experience for developers using the Chat Channel Sample who are not using Unity Game Services.
- Enabled bitcode configuration for build output that prevented developers from archiving Xcode builds on iOS.

### Added

- Added a DeviceEnergy property to AudioOutputDevices.cs and AudioInputDevices.cs

### Changed

- Adjusted Vivox's default AVAudioSession values on iOS to provide improved volume-related behavior.

## [15.1.150002-pre.2] - 2021-10-20

### Fixed

- Chat Channel Sample was not pulling in its Authentication package dependency. The Authentication package is now added to the project if it is not already there.

## [15.1.150002-pre.1] - 2021-10-06

### Added

- For com.unity.services.vivox users, new Channel and Account classes should replace ChannelId and AccountId, respectively.
- Updated Debug Token Generation to be overridden with Auth JWT generation if the Authentication package is in use.
- Added a warning for Apple silicon builds which notes that Vivox does not work. macOS users must set their Unity target platform architecture to Intel 64-bit.
- Added an Editor script to broadcast a warning if a conflicting Unity Asset Store package is loaded in a project.

### Changed

- Updated the Chat Channel Sample to properly use VivoxSettings credentials.
- Modified channel session deletion to use channel state events. Connected channels can now be safely deleted when connected.
- Updated the Services menu to redirect to the Vivox Project Settings.
- Updated the code snippet example for signing in and joining an echo channel in the Vivox Unity SDK QuickStart documentation to use plain bools instead of checks against the enum.
- Revised various engine startup warnings.
- Shortened autogenerated file names.

## [15.1.150000] - 2020-08-02

### Added

- New Vivox Credential manager in Project/Settings/Services/Vivox
- Dependency on com.unity.services.core in our new Unity.Services.Vivox namespace
- New way to initialize Vivox allow side all other Game Services
- Leverage Unity Project Environments

## [5.15.0-preview] - 2020-06-03

### Changed

- First transition from our old Unity Asset Store Package to a UPM Package com.unity.services.vivox
