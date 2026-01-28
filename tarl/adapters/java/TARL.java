public final class TARL {
    public final String version = "2.0";
    public final String intent;
    public final String scope;
    public final String authority;
    public final String[] constraints;

    public TARL(String intent, String scope, String authority, String[] constraints) {
        this.intent = intent;
        this.scope = scope;
        this.authority = authority;
        this.constraints = constraints;
    }
}
