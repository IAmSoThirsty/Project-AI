# Readme

README - User Generated Content Sample Scenes - Content Browser

## Overview

In this example, you will learn how you could leverage the Creator Economy SDK to display a User Generated Content browser in-app.

This sample uses a prefab called the Content Browser, which is a sample UI hierarchy in-scene which can populate itself with content retrieved from the server. It would allow a
user to view, subscribe to, rate, report and play User Generated Content (UGC).

The SDK currently only allows connection to the services required in Play mode, but this can still be used with Play-In Editor.

## How this sample leverages the SDK

### Connection to Unity Game Services

The Content Browser script (see below) is able to handle the connection to Unity Game Services for the app. It can be configured to target whichever environment is needed. If this
sample is integrated into an existing app, the automatic connection to Unity Game Services here can be disabled in favour of how the aforementioned app handles the connection.
Please note that a connection to Unity Game Services is required for this sample, as well as any application of User Generated Content, to function in an app.

### Implementation of User Generated Content

Most of the implementation of User Generated Content in handled in the Content Browser itself, or in the Content Dialog View, where the user can interact with the User Generated
Content. The `Content` class of the UGC SDK is of particular import, as that is the synchronizable data model of the Content itself. Other usages include individual content views.

#### Content Browsing

 - The Content Browser contains the set of content filtered first by whether or not viewing all content or subscribed content. Content lists are first obtained via either

 `UgcService.Instance.GetContentsAsync` or `GetSubscriptionsAsync`, depending on the user's chosen Header Tab. For each of the `PagedResults` obtained from the aforementioned
 call, detailed `Content` results are gathered via `UgcService.Instance.GetContentAsync`.

#### Featured Content

 - The Featured Content View first gets the list of featured content via `UgcService.Instance.GetContentsAsync`, passing in a `GetContentsArgs` which is a structure containing

 the various tags by which to filter said content. The results are a set of `PagedResults`, but only one page's worth.

 - The Featured Content View, and in any given Featured Content Button, the content will be set by calling `UgcService.Instance.DownloadContentDataAsync`, which will then get the

 `Content` object and apply the thumbnail to the button image.

 - Additionally, the Featured Content View allows the user to directly view and manipulate the subscription to content, via `UgcService.Instance.IsSubscribedToAsync`,

 `DeleteSubscriptionAsync`, and `CreateSubscriptionAsync`.

#### Content Cards

 - Much like the Featured Content section above, the Content Card View will set its `Content` by calling `UgcService.Instance.DownloadContentDataAsync`, which will then get the

 `Content` object and apply the thumbnail to the card image. Additionally, as with the Featured Content, the Content Card allows the user to directly manipulate the subscription to content, via
 `UgcService.Instance.IsSubscribedToAsync`, `DeleteSubscriptionAsync`, and `CreateSubscriptionAsync`.

#### Content Dialog View

 - Similar to the Content Cards above, The Content Dialog View will leverage `UgcService.Instance.DownloadContentDataAsync` to download the content and apply the Thumbnail.
 - In addition to gett and manipualiating the subscription status via `UgcService.Instance.IsSubscribedToAsync`, `DeleteSubscriptionAsync`, and `CreateSubscriptionAsync`, the user

 can rate or report the Content. Ratings, wrapped by `ContentUserRating`, are checked and modified via `UgcService.Instance.GetUserContentRatingAsync` and
  `UgcService.Instance.SubmitUserContentRatingAsync` respectively. Likewise content can be reported via `UgcService.Instance.ReportContentAsync`, passing in `ReportContentArgs`.


## Content Browser Prefab

 The following is an overview of the Content Browser Prefab itself and what each of the sample's Monobehaviour or UI Component classes do.

### Related Scripts:

#### Content Browser

 Main script to bind and control the contents of the prefab. Upon starting, it will initialize its content group view with
 the Content per page, refresh the tabs to ist curent state and bind UI events. If set, it will initialize UGS Services and
 refresh content in kind. When it refreshes content, it will asynchronously fetch content from the UGC service.

**Configurable Fields:**

 - Skip Services Initialization (boolean allowing you to skip auto initialization and do that manually in your own code)
 - Service Environment Name (The UGS service environment, `"production"` by default)
 - Content per Page (number of UGC items per page, `8` by default)

**Pre-Assigned Game Objects:**

 - UI Root - the Root UI node, used to simply show or hide the whole UI hierarchy
 - Content Libraries Root - Active when the Libraries Header tab is selected
 - Content Dialog Root - Active when the Content Dialog Header tab is selected

**Pre-Assigned Views:**

 - Header View
 - Content Search View
 - Featured Content View
 - Content Group View
 - Content Pagination View
 - Content Dialog View

#### Content Card View

 Detailed view of a User Generated Content item

 **Auto-Assigned Action:**

  - On View Content Event - Event triggered when the content is selected

 **Populable Fields:**

  - Raw Content Image - Thumbnail reperesenting the Content
  - Content Name Label - UI element containing the Content's name
  - Content Description Label - UI element containing the Content's description
  - Subscription Stat - UI element containing the number of subscribers
  - Rating Stat - UI element containing the number of rating
  - Report Stat - UI element containing the number of reports as being inappropriate

#### Content Dialog View

 Interactive View of a given User Generated Content, allowing the user to view, rate, play, subscribe to or report it.

 **Pre-Assigned UX Elements:**

  - Close Button - Closes the Dialog
  - Rate Button - Allows the user to rate the content
  - Report Button - Allows the user to report the content (DMCA, Non-Functional, Inappropriate, Illegal, Misleading, Other)
  - Subscription Button - Allows the user to subscribe to the content
  - Play Button - Allows the user to play the content

 **Populable Fields:**

  - Raw Content Image - Thumbnail reperesenting the Content
  - Content Name Text - UI element containing the Content's name
  - Content Description Text - UI element containing the Content's description
  - Subscription Text - UI element containing the number of subscribers
  - Rating Text - UI element containing the number of rating
  - Report Text - UI element containing the number of reports as being inappropriate
  - Updated Text - UI element containing the last update date

#### Content Group View

 Groups Content Card Views in a row. It will instantiate one Instance of the Content Browser Cell prefab for each content
 to be displayed on a page of the Content Browser.

**Pre-Assigned Fields:**

 - Content Card View Prefab - Instance of the Content Browser Cell Prefab, which is used to instantiate Content Card Views and their associated game objects

#### Content Library Type

 - Enum coding for either `AllContent`, or `Subscribed` content - Applies to Heaver View Buttons and the contents of the Content Browser.

#### Content Pagination View

 View to facilitate the pagination of content - Allows quick navigation to another page of content.

**Configurable Fields:**

 - Max Pages Displayed - The cap on the number of pages that can be shown

**Pre-Assigned UX Fields:**

 - Previous Page Button - Page button to go back a page
 - Next Page Button - Page button to go forward a page
 - Start Truncated Icon - An icon to indicate that the user is not at the beginning of the Page buttons Group
 - End Truncated Icon - An icon to indicate that the user is not at the end of the Page buttons Group
 - Page Button Template - Template of a numbered page button to be instantiated into the Page Buttons Group. Not a Prefab.
 - Page Buttons Group - A horizontally laid out list of Page Buttons that quickly jump to a page number.

#### Content Search View

 Search Interface to look for content via a string and then order the results. Searching will refresh the view of entries within the Content Browser.

**Pre-Assigned UX Fields:**

 - Search Field - The text box in which the user can enter a search string
 - Refresh Button - A button to refresh the search results
 - Sort-By Dropdown - A dropdown to order the search result by various criteria (Popularity, Rating, New, Updated or Alphabetical)

#### Counter Button

 - Button used to accumulate a vote counter from users. A single user can toggle it on or off, which will add or subtract

their vote. Used for Like/Dislike Ratings, or for reporting inappropriate content in the Content Dialog View.

#### Featured Content Button

 - Button to select featured content. Will be assigned a thumbnail of the previous and the next content page in the Featured Content View.

#### Featured Content Card View

 - Element of the Featured Content View that displays the details of featured content as a clickable item

**Populable Fields:**

 - Content Name Label - Name of the User Generated Content
 - Content Raw Image - Thumbnail of the User Generated Content

**Pre-Assigned UX fields:**

 - View Button - Clickable element of the Card to view the content in the Content Browser
 - Subscribe Button - Subscription Button to subscribe to this content

#### Featured Content View

 Wrapper for a Featured Content Card View and its navigation buttons. This allows the user to click a feature card to view the content
 in the Content Browser's Content Dialog View. Featured content is currently hard-coded to be pre-sorted by popularity.

**Pre-Assigned UX Fields:**

 - Featured Content Count - Limit on how much featured content to display (default 5, from 1-25).
 - Featured Content Card View - Instance of the Featured Content Card View class. Clicking on this will show the content of the Card in the Content Browser.
 - Previous Card Button - Featured Content Button to scroll back to the previous Featured Content Card View.
 - Next Card Button - Featured Content Button to scroll back to the next Featured Content Card View.

#### Header View

 UI View of the Header of the Content Browser - Allows the user to close to toggle between all or subscribed content and also
 to the browser itself. Will display the name of your game or app.

**Pre-Assigned UX Fields:**

 - Game Name Label - Enter the name of your game or app in the linked element here
 - All Content Tab Button - Header Tab Button that will toggle to show all content once pressed
 - Subscribed Tab Button - Header Tab Button that will toggle to show all content once pressed
 - Close Content Browser Button - Button to close the entire Content Browser

#### Header Tab Button

 - Tabs on the header above the content, representing `AllContent`, or `Subscribed` content in the Header View class.

#### Page Button

 - Button to change pages of content, used in the Content Pagination View.

#### Subscription Button

 - Toggles a user's Subscription to content. Used in the Content Card View, Content Dialog View or Featured Content View.

## Content Browser Cell Prefab

 - A prefab used to instantiate Content Card Views with associated GameObject Hierarchy for its UX.
