# Remote Config files

## Creation

Right-click the Project Window, then select `Assets > Create > Remote Config` to create a Remote Config file.

## File Format

For the files to be properly parsed they need to respect the json schema that can be found here: https://ugs-config-schemas.unity3d.com/v1/remote-config.schema.json

### Example

Following example contains 3 keys:

1. A string key "name"
2. An long key "id"
3. A json key "user_schema"

```json
{
  "$schema": "https://ugs-config-schemas.unity3d.com/v1/remote-config.schema.json",
  "entries": {
    "name": "example_name",
    "id": "10000000000",
    "user_schema": {
        "user_id_key": "user_id",
        "user_name_key": "user_name"
    }
  },
  "types": {
      "id": "LONG"
  }
}
```

## File Deployment

Once created, files can be deployed to the environment selected. To deploy a file go to `Window > Deployment` (2021.3+) or `Services > Deployment` (2022+).
Once opened, the Deployment Window will display all of your local remote config files and enable you to deploy them.
For more information on the expected deployment window workflow, please consult the ["com.unity.services.deployment"](https://docs.unity3d.com/Packages/com.unity.services.deployment@latest) package's documentation.
