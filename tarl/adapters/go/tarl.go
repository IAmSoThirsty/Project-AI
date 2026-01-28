package tarl

type TARL struct {
    Version     string   `json:"version"`
    Intent      string   `json:"intent"`
    Scope       string   `json:"scope"`
    Authority   string   `json:"authority"`
    Constraints []string `json:"constraints"`
}

func New(intent, scope, authority string, constraints []string) TARL {
    return TARL{
        Version: "2.0",
        Intent: intent,
        Scope: scope,
        Authority: authority,
        Constraints: constraints,
    }
}
