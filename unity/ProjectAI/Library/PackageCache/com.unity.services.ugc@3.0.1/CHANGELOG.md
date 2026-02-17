# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [3.0.1] - 2024-04-25

- Added Apple privacy manifest to comply with Apple's new privacy requirements. More details on how the Unity Engine supports this can be found [here](https://forum.unity.com/threads/apple-privacy-manifest-updates-for-unity-engine.1529026/).
- Upgraded `com.unity.services.core` from 1.9.0 to 1.12.5 to include their Apple privacy manifest.
- Upgraded `com.unity.services.authentication` from 2.5.0 to 3.3.1 to include their Apple privacy manifest.

## [3.0.0] - 2023-11-16

### Changed

- `GetTagsAsync` changed to only returns tags for the current environment.
- New or updated public content will now be `public` instead of `publicGlobal`

## [2.0.0] - 2023-10-20

### Added

- Added `ContentVisibility` options: `public` and `unlisted`

### Changed

- Deprecated `ContentVisibility` options: `publicGame` and `publicGlobal`. Use `public` instead.
- Upgraded `com.unity.services.core` from 1.7.1 to 1.9.0
- Upgraded `com.unity.services.authentication` from 2.4.0 to 2.5.0
- Updated Quick Start Guide and API documentation.

### Removed

**BREAKING CHANGES**

- Removed `OwnerAccountId` from `ContentDTO` model.
- Removed `ContentDownloadStatistics` from `ContentStatistics` model.
- Removed `Subscribers` from `ContentStatistics` model.
- Removed `ContentReportStatistics` from `ContentStatistics` model.
- Removed `ContentRatingStatistics` from `ContentStatistics` model.
- Removed `ContentPortalVisitStatistics` from `ContentStatistics` model.

## [1.0.0-pre.10] - 2023-04-19

### Changed

- License update
- Fixed compile error in Content Browser sample when building the project

## [1.0.0-pre.9] - 2023-04-18

### Changed

- Changed `GetContentTrendsArgs` to match other model classes
- Updated `SearchContentSortBy` with the correct fields for content statistics
- Updated the Content Browser sample with the latest updates/fixes

## [1.0.0-pre.8] - 2023-04-12

### Added

- Added a content browser prefab that can be imported as sample from the package manager.
- Added `BaseSearchArgs` to simplify all RequestArgs class used in search requests and also reorganized SortBys enums.
- Added `GetContentTrendsAsync` in `WrappedUgcService` and `GetContentTrendsArgs`.
- Added `DiscoveryTags` in `Content` model.
- Added `RatingsAverage`, `RatingsCount`, `DownloadsCount`, `SubscriptionsCount` and `ReportsCount` to `ContentStatistics`.

### Changed

- Changed `Owner` name to `Creator` across the SDK.
- Deprecate `Downloads`, `Subscribers`, `Reports`, `Ratings`, `PortalVisits` and `RatingsAverage`from `ContentStatistics`.

### Removed

**BREAKING CHANGES**

- Removed `ReportsCount` from `Content` model.
- Removed `ReportType` from `GetContentsArgs`.

## [1.0.0-pre.7] - 2023-02-16

### Added

- Added `GetPlayerContentsAsync` and `GetPlayerContentsArgs` to expose `SearchPlayerContentAsync` from ContentAPI.
- Added `PagedResults<T>` for search APIs results.
- Added `ApproveContentAsync`, `RejectContentAsync` and `SearchContentModerationAsync` from the ModerationAPI.

### Changed

**BREAKING CHANGES**

- Changed `GetContentsAsync`, `GetContentVersionsAsync`, `GetRepresentationsAsync`, `GetRepresentationVersionsAsync`, `GetSubscriptionsAsync` and `SearchRepresentationsAsync` return type to `PagedResult<T>` to include pagination information.
- Moved `Tag`, `Subscription`, `RepresentationVersion`, `RepresentationTag`, `Representation`, `ContentVersion`, `ContentUserRating` and `Content` out of the namespace Unity.Services.Ugc.Models into Unity.Services.Ugc.
- Unity.Services.Ugc.Models namespace was removed.
- Changed return value of `ReportContentAsync` to return the reported content.

## [1.0.0-pre.6] - 2022-11-16

### Added

- Added `ContentStatistics`, which includes `ContentDownloadStatistics`, `Subscribers`, `ContentReportStatistics`, `ContentRatingStatistics` and `ContentPortalVisitStatistics`

**BREAKING CHANGES**

- Replaced `ContentDownloadStatistics` for `ContentStatistics` in `Content`

## [1.0.0-pre.5] - 2022-11-10

### Added

- Added `IncludeStatistics` field in `GetContentArg`
- Added ContentDownloadStats `DownlodStatistics` in `Content` model

**BREAKING CHANGES**

- Added `IncludeTotal` field in `GetContentsArgs`, `GetContentVersionArgs`, `GetRepresentationArgs`, `GetRepresentationVersionArgs`, `GetSubscriptionsArgs` and `SearchRepresentationArgs`.

## [1.0.0-pre.4] - 2022-09-29

### Added

- Added `CustomId` and `Metadata` fields `CreateContentArgs` for content customization
- Added `GetContentVersionsAsync` in order to retrieve all the content versions of a given content
- Added Representation API (Create, Update, Delete, Search) to handle different representations of a given content

### Changed

- Updated the license.
- Thumbnail is now optional with `CreateContentVersionAsync`
- Updated Core dependency to 1.4.0

**BREAKING CHANGES**

- Removed thumbnail parameter from `CreateContentArgs` constructor as it's now optional.
- Changed minimum supported version from 2019.4 to 2020.3

## [1.0.0-pre.3] - 2022-05-02

### Changed

**BREAKING CHANGES**

- Moved `SetBasePath` to `UgcServiceSDKUtils.SetBasePath`
- Moved all `CreateContentAsync` parameters to the class `CreateContentArgs`
- Renamed `GetContentOptions` to `GetContentArgs` and moved `contentId` parameter into that class.
- Renamed `TagDTO` to `Tag`
- Renamed `ContentUserRatingDTO` to `ContentUserRating`
- Renamed `UgcServiceSDKUtils` to `UgcServiceSdkUtils`

## [1.0.0-pre.2] - 2022-04-06

### Added

- Added quickstart documentation to provide enough information to start using UGC package.

## [1.0.0-pre.1] - 2022-04-01

### Added

- Added `UgcException` exception which is thrown by UGC Api methods to better understand why a request failed. List of error codes can be found within `UgcErrorCodes`.
- Added `ratingCount` and `subscriptionCount` fields to `ContentDTO` to indicate how many ratings and subscribers a content has.
- Added `UpdateContentDetailsAsync` to update the content metadata after it has been created
- Added `ReportContentAsync` to let the end-user report a specific content to moderation
- Added `CreateSubscriptionAsync` to subscribe the current user to a content
- Added `DeleteSubscriptionAsync` to remove the current user's subscription to a content (if it exists)
- Added `IsSubscribedToAsync` to check if the current user is subscribed or not to a content
- Added `GetSubscriptionsAsync` to fetch the current user subscriptions list (results can be sorted/filtered)
- Added `DownloadContentDataAsync` to get the data (asset/thumnbnail) of an already fetched content

### Changed

- Added visibility option to `CreateContentAsync`, by passing true or false to the parameter `isPublic` users can create public or private content.
- Added `enabled` field to `ProjectDTO` to see if a project is publicly visible in the UGC portal
- Added `AssetUploadStatus` and `ThumbnailUploadStatus` to `ContentDTO` to show the status of their upload after a call to `CreateContent` and `CreateContentVersion`
- Added `GetContentOptions` to `GetContent` to be able to download the data and the thumbnail with the same call

**BREAKING CHANGES**

- Renamed `UGC` to `UgcService`. Access to the service is now done through `UgcService.Instance`.
- Changed `UgcService.Instance` to return `IUgcService` instead of `WrappedUGCService`.
- Changed `WrappedUGCService` visibility to `internal` and renamed to `WrappedUgcService`.
- Renamed `GetContents` to `GetContentsAsync`
- Changed `GetContentsAsync` signature, now all details of the request need to be added through an instance of `GetContentsArgs`. Exposed `Offset` and `Limit` fields and also added `AddSortBy` method making the search request more complete.
- Renamed `GetContent` to `GetContentAsync`
- Renamed `CreateContent` to `CreateContentAsync`
- Renamed `CreateContentVersion` to `CreateContentVersionAsync`
- Renamed `DeleteContent` to `DeleteContentAsync`
- Renamed `GetTags` to `GetTagsAsync`
- Renamed `GetUserContentRating` to `GetUserContentRatingAsync`
- Renamed `SubmitUserContentRating` to `SubmitUserContentRatingAsync`
- Refactored `TagDTO` to only have `id` and `name` fields (`id` was previously an int and is now a string). `CreateContentAsync` was updated to reflect the change, the required type is now `List<string>` for its `tags` parameter.
- Renamed `optimisticContentDTO` from `ContentDTO` to `content`
- Changed `ContentDTO` to `Content`. `ThumbnailUrl` and `DownloadUrl` were removed. `Content` has `DownloadedThumbnail` and `DownloadedContent` fields that will be filled with the corresponding data through either `GetContent` with `GetContentOptions` or with `DownloadContentDataAsync`
- Changed `SubscriptionDTO` to `Subscription`
- Changed `VisibilityOption` to `ContentVisibility`
- Changed `ReviewRuleOptions` to `ProjectReviewRule`
- Changed asset and thumbnail upload status enum to `ContentUploadStatus`

## [0.0.3-preview] - 2022-02-18

### Added

- Added Tag support to `ContentDTO`. You can use `UGC.Instance.GetTags` to fetch all tags of a project. Tags are labels users can add to a content to help categorize it.
- Added `UGC.Instance.GetUserContentRating` to get the rating a player gave to a specific content.
- Added MD5 content hashes of thumbnail `thumbnailMd5Hash` and content `contentMd5Hash` to `ContentDTO`. A hash changes whenever the content of its file changes and can help you cache the data more efficiently.
- Added a boolean flag `IsUserSubscribed` to `ContentDTO` to indicate whether or not the current player is subscribed to that content.

### Changed

**BREAKING CHANGES**

- Changed `UGC.Instance.CreateContent` to streamline the content creation process. It now returns an eventually consistent `ContentDTO` containing the upload URLs to the thumbnail and content location; it will not show up in search or in GetContents until both items are done being uploaded.
- Changed `UGC.Instance.CreateContentVersion` which now acts the same way as `UGC.Instance.CreateContent` but for a new version of a content.
- Renamed `GetContent` to `GetContents` for the version returning all the contents.
- Removed the `projectId` and `environmentId` parameters from all API methods. It now uses the project and environment the player is logged in to.
- Changed how to override the Environment used by the API, use `InitializationOptions.SetEnvironmentName` to specify the name, rather than the id of the environment you want to use.
- Renamed `ContentDTO.ContentId` to `ContentDTO.Id`.
- `ContentDTO.ReportsCount` is now null.

### Bugfixes

- Fixed a bug which caused the API to become unresponsive after two hours.

## [0.0.2-preview] - 2022-01-25

### Bugfixes

- Fixed a bug which caused content creation to fail when using a Unity project environment that is not the default one.
- Fixed a bug which caused content from all environments to show up when searching in specific environment.

## [0.0.1-preview] - 2022-01-17

### This is the first release of *com.unity.services.ugc*.

- Create a content
- Create a content version (upload)
- Get the latest version of a content
