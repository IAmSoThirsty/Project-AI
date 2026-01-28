public record TARL(
    string Intent,
    string Scope,
    string Authority,
    string[] Constraints
) {
    public string Version => "2.0";
}
