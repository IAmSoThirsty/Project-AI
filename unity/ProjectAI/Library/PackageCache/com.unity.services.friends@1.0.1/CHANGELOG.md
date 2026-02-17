# Changelog

All notable changes to this package will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

## [1.0.1] - 2024-04-30

* Added apple privacy manifest
* Updated com.unity.services.core to 1.12.5
* Updated com.unity.services.authentication to 2.7.4
* Updated com.unity.services.wire to 1.2.5


## [1.0.0] - 2023-10-15

## [1.0.0-pre.5] - 2023-10-06

### Changed

- Updated com.unity.services.wire dependency to 1.2.2

## [1.0.0-pre.4] - 2023-09-20

### Changed

- Changed deserialization strategy for custom `Activity` and `Message` objects, this will allow for new message members of a payload to not throw an exception.

### Fixed

- Fixed an issue where `MessageAsync` was not throwing the correct type of error
- Fixed an issue where in certain rare occurances the incorrect `HttpStatusCode` would be passed in `FriendsServiceException`

## [1.0.0-pre.3] - 2023-09-07

This update has some renames and functionality changes that make the code clearer.
The sample asset has been update in this [PR](https://github.com/Unity-Technologies/com.unity.services.samples.friends/pull/45) and is an
example of what to expect for the rename.

### Added

- Added `RelationshipNotFoundException` to describe relationship not found in the local storage

### Changed

- Updated com.unity.services.authentication dependency to 2.5.0
- Updated com.unity.services.wire dependency to 1.2.0
- Updated naming to improve consistency across the package, renaming instances of Relationship to Friends where it made sense
    - Deprecated `RelationshipServiceException` in favor of `FriendsServiceException`
    - Deprecated `RelationshipErrorCode` in favor of `FriendsErrorCode`
    - Deprecated `PresenceAvailabilityOptions` in favor of `Availability`
- Updated XML documentation to be more consistent with naming and have better descriptions
- Updated Enums to be PascalCase instead of UPPERCASE

### Fixed

- Fixed IncomingFriendRequests showing requests from blocked users
- Fixed OutgoingFriendRequests showing requests from blocked users
- Fixed Exception handling to have more accurate data with regards to status codes

## [1.0.0-pre.1] - 2023-03-14

### Added

### Changed

- Updated package version for Open Beta
- Removed unnecessary error codes

### Fixed

## [0.2.0-preview.9] - 2023-03-13

### Added

- Added AddFriendByNameAsync allowing the addition of a friend using their name provided it comes from the player names service
- Added validation to make sure the service can only be used once the user is signed in.
- Added validation to make sure the service must be initialized <code>await FriendsService.Instance.InitializeAsync();</code> before it is used. Note that <code>InitializeAsync()</code> should only be called once after signing in.

### Changed

- Changed name of ManagedRelationshipsService to FriendsService in order to maintain consistency with the product's name.
- Changed the way the interaction with the service is handled. It now uses the singleton pattern to adhere to Unity SDK standards.

Before:

<code>
var service = await ManagedRelationshipService.CreateManagedRelationshipServiceAsync();

await service.AddFriendAsync(memberId);
</code>

After:

<code>await FriendsService.Instance.InitializeAsync();

await FriendsService.Instance.AddFriendAsync(memberId);
</code>

- Updated the way data is accessed from events to mostly use properties instead of functions.
- Updated properties returned by the FriendsService to IReadOnlyList.

### Fixed

## [0.2.0-preview.8] - 2023-03-01

### Added

- Implemented message feature (Intended usage example: lobby integration, sending lobby join codes between friends)

### Changed

- Minor updates to XML docs

### Fixed

## [0.2.0-preview.7] - 2023-01-11

### Added

### Changed

- Updated enums that are not flags to not have their values with bitshift operation
- Updated return of Friends property for managed relationship service to return list of friends that do not have blocks with the same user
- Updated readme docs

### Fixed

## [0.2.0-preview.6] - 2022-12-12

### Changed

- Fixed bug with deserialization issue for presence updated events

## [0.2.0-preview.5] - 2022-12-09

### Added

- More updates to the documentation

### Changed

- Regenerated SDK code with new OpenAPI changes that removed a good amount of unused objects
- Updated code and tests to reflect the changes from the regenerated code. No breaking changes to the user interface, all changes were internal only

### Fixed

## [0.2.0-preview.4] - 2022-11-17

## Added

### Changed

- Removed SubscribeToEventAsync in favor of individual event callbacks now in IManagedRelationshipService
- Significant updates to Documentation

### Fixed

## [0.2.0-preview.3] - 2022-11-10

### Added

- Enabled event support in the `ManagedRelationshipService`

-

### Changed

### Fixed

## [0.2.0-preview.2] - 2022-11-01

### Added

### Changed

- Removed `/friends` APIs and merged them all into `/relationships` APIs.
- Updated wire notifications to include relationships data.
- Annotate present and profile data.
- Many other fixes and updates.

### Fixed

## [0.1.0-preview.54] - 2022-08-12

### Added

- Working prototype of the Friends SDK package.

### Changed

### Fixed
