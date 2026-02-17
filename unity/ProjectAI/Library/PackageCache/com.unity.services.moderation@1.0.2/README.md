# Moderation

Unity Moderation aims to make toxicity-management accessible, impactful, and insightful – providing developers with the
tools they need to grow and maintain healthy communities within their games.

## Prerequisites

Full setup steps are available on the
main [Moderation Service documentation](https://docs.unity.com/ugs/en-us/manual/moderation/manual/overview).
You can find pre-requisite steps [here](https://docs.unity.com/ugs/en-us/manual/moderation/manual/get-started). A full
list of game and player requirements are
available [here](https://docs.unity.com/ugs/en-us/manual/moderation/manual/requirements).

After completing the above, you can continue on to using the SDK. Full-detailed documentation is
available [here](https://docs.unity.com/ugs/en-us/manual/moderation/manual/moderation-sdk).

## Using the SDK

The Moderation SDK depends on the Operate Core SDK.

To use the SDK you must initialize the Operate Core SDK, and be authenticated.

```csharp
using Unity.Services.Authentication;
using Unity.Services.Core;
using Unity.Services.Moderation;
using Unity.Services.Moderation.Models;
```

```csharp
try
{
    await UnityServices.Initialize();
    await AuthenticationService.Instance.SignInAnonymouslyAsync();
}
catch (Exception e)
{
    Debug.Log(e);
}
```

You should then be able to access the Moderation SDK using a singleton interface:

```csharp
var report = Moderation.Instance.NewReport("player-id",
                new ReportReason(ReportReason.Hacking));

await Moderation.Instance.ReportPlayer(report);
```
