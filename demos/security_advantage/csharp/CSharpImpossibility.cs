 /*
 * C# Security Demonstration: Why Absolute Secret Protection is IMPOSSIBLE
 * 
 * C# Version: 12 (.NET 8)
 * Updated: 2026 with modern features
 * 
 * This demonstrates that C# CANNOT provide absolute protection for secrets,
 * even with best practices and modern features, due to fundamental architectural constraints.
 * 
 * The Challenge: Protect an API key so that even with full access to the .NET
 * runtime, an attacker cannot extract it.
 * 
 * Result: IMPOSSIBLE in C# - all protection mechanisms can be bypassed.
 * 
 * Build: dotnet build
 * Run: dotnet run
 */

using System;
using System.Reflection;
using System.Runtime.InteropServices;
using System.Runtime.CompilerServices;
using System.Security;
using System.Text;

class CSharpImpossibility
{
    static void Main()
    {
        Console.WriteLine("=".PadRight(80, '='));
        Console.WriteLine("C# SECRET PROTECTION: IMPOSSIBLE TO ACHIEVE ABSOLUTE SECURITY");
        Console.WriteLine($".NET {Environment.Version} | C# 12");
        Console.WriteLine("=".PadRight(80, '='));
        Console.WriteLine();

        Attempt1_PrivateField();
        Attempt2_ReadonlyField();
        Attempt3_PropertyWithPrivateBackingField();
        Attempt4_SecureString();
        Attempt5_PrimaryConstructors();
        Attempt6_CollectionExpressions();
        Attempt7_RefReadonlyParameters();
        Attempt8_UnsafePointers();
        Attempt9_InternalModifier();
        Attempt10_Interceptors();

        PrintSummary();
    }

    // ========================================================================
    // ATTEMPT 1: Private Field with Encapsulation
    // ========================================================================
    static void Attempt1_PrivateField()
    {
        Console.WriteLine("ATTEMPT 1: Private Field Encapsulation");
        Console.WriteLine("-".PadRight(80, '-'));

        var holder = new PrivateFieldSecret("sk-PRODUCTION-SECRET-12345");
        
        // Bypass: Use reflection to access private field
        var fieldInfo = typeof(PrivateFieldSecret).GetField("_apiKey", 
            BindingFlags.NonPublic | BindingFlags.Instance);
        var extractedSecret = (string)fieldInfo.GetValue(holder);
        
        Console.WriteLine($"✗ BYPASSED (Reflection): {extractedSecret}");
        Console.WriteLine("  Attack: Reflection API bypasses access modifiers");
        Console.WriteLine();
    }

    class PrivateFieldSecret
    {
        private readonly string _apiKey;
        
        public PrivateFieldSecret(string apiKey)
        {
            _apiKey = apiKey;
        }
        
        public string GetKey() => _apiKey;
    }

    // ========================================================================
    // ATTEMPT 2: Readonly Field
    // ========================================================================
    static void Attempt2_ReadonlyField()
    {
        Console.WriteLine("ATTEMPT 2: Readonly Field (Immutability)");
        Console.WriteLine("-".PadRight(80, '-'));

        var holder = new ReadonlyFieldSecret("sk-PRODUCTION-SECRET-12345");
        
        // Bypass: Reflection can modify readonly fields
        var fieldInfo = typeof(ReadonlyFieldSecret).GetField("_apiKey",
            BindingFlags.NonPublic | BindingFlags.Instance);
        
        var extractedSecret = (string)fieldInfo.GetValue(holder);
        Console.WriteLine($"✗ BYPASSED (Reflection): {extractedSecret}");
        
        // Even modification is possible!
        fieldInfo.SetValue(holder, "HACKED");
        Console.WriteLine($"✗ MODIFIED readonly field: {holder.GetKey()}");
        Console.WriteLine("  Attack: Reflection bypasses readonly enforcement");
        Console.WriteLine();
    }

    class ReadonlyFieldSecret
    {
        private readonly string _apiKey;
        
        public ReadonlyFieldSecret(string apiKey)
        {
            _apiKey = apiKey;
        }
        
        public string GetKey() => _apiKey;
    }

    // ========================================================================
    // ATTEMPT 3: Property with Private Backing Field
    // ========================================================================
    static void Attempt3_PropertyWithPrivateBackingField()
    {
        Console.WriteLine("ATTEMPT 3: Property with Private Backing Field");
        Console.WriteLine("-".PadRight(80, '-'));

        var holder = new PropertySecret("sk-PRODUCTION-SECRET-12345");
        
        // Bypass 1: Access auto-generated backing field
        var backingField = typeof(PropertySecret).GetField("<ApiKey>k__BackingField",
            BindingFlags.NonPublic | BindingFlags.Instance);
        
        if (backingField != null)
        {
            var extractedSecret = (string)backingField.GetValue(holder);
            Console.WriteLine($"✗ BYPASSED (Backing Field): {extractedSecret}");
        }
        
        // Bypass 2: Access through property getter
        var propertyInfo = typeof(PropertySecret).GetProperty("ApiKey",
            BindingFlags.NonPublic | BindingFlags.Instance);
        var secretViaProperty = (string)propertyInfo.GetValue(holder);
        Console.WriteLine($"✗ BYPASSED (Property): {secretViaProperty}");
        Console.WriteLine("  Attack: Auto-properties still use accessible fields");
        Console.WriteLine();
    }

    class PropertySecret
    {
        private string ApiKey { get; set; }
        
        public PropertySecret(string apiKey)
        {
            ApiKey = apiKey;
        }
    }

    // ========================================================================
    // ATTEMPT 4: SecureString (Microsoft's "Secure" Solution)
    // ========================================================================
    static void Attempt4_SecureString()
    {
        Console.WriteLine("ATTEMPT 4: SecureString (Microsoft's Security Class)");
        Console.WriteLine("-".PadRight(80, '-'));

        var secureSecret = CreateSecureString("sk-PRODUCTION-SECRET-12345");
        
        // Bypass: Marshal to extract from SecureString
        IntPtr ptr = Marshal.SecureStringToBSTR(secureSecret);
        try
        {
            var extractedSecret = Marshal.PtrToStringBSTR(ptr);
            Console.WriteLine($"✗ BYPASSED (Marshal): {extractedSecret}");
        }
        finally
        {
            Marshal.ZeroFreeBSTR(ptr);
        }
        
        // Bypass 2: Direct unsafe memory access
        IntPtr ptr2 = Marshal.SecureStringToGlobalAllocUnicode(secureSecret);
        try
        {
            var extractedSecret2 = Marshal.PtrToStringUni(ptr2);
            Console.WriteLine($"✗ BYPASSED (Unsafe Memory): {extractedSecret2}");
        }
        finally
        {
            Marshal.ZeroFreeGlobalAllocUnicode(ptr2);
        }
        
        Console.WriteLine("  Attack: SecureString must be converted to string for use");
        Console.WriteLine("  Note: SecureString is deprecated in .NET 5+");
        Console.WriteLine();
    }

    static SecureString CreateSecureString(string value)
    {
        var secure = new SecureString();
        foreach (char c in value)
            secure.AppendChar(c);
        secure.MakeReadOnly();
        return secure;
    }

    // ========================================================================
    // ATTEMPT 5: Primary Constructors (C# 12)
    // ========================================================================
    static void Attempt5_PrimaryConstructors()
    {
        Console.WriteLine("ATTEMPT 5: Primary Constructors (C# 12 Feature)");
        Console.WriteLine("-".PadRight(80, '-'));

        var holder = new PrimaryConstructorSecret("sk-PRODUCTION-SECRET-12345");
        
        // Bypass: Access captured parameter field
        var fieldInfo = typeof(PrimaryConstructorSecret).GetField("apiKey",
            BindingFlags.NonPublic | BindingFlags.Instance);
        
        if (fieldInfo != null)
        {
            var extractedSecret = (string)fieldInfo.GetValue(holder);
            Console.WriteLine($"✗ BYPASSED (Parameter Capture): {extractedSecret}");
        }
        
        // Bypass 2: Call the public method
        Console.WriteLine($"✗ BYPASSED (Method Call): {holder.GetKey()}");
        Console.WriteLine("  Attack: Primary constructor parameters captured as private fields");
        Console.WriteLine();
    }

    // C# 12: Primary constructor syntax
    class PrimaryConstructorSecret(string apiKey)
    {
        public string GetKey() => apiKey;
    }

    // ========================================================================
    // ATTEMPT 6: Collection Expressions (C# 12)
    // ========================================================================
    static void Attempt6_CollectionExpressions()
    {
        Console.WriteLine("ATTEMPT 6: Collection Expressions (C# 12 Feature)");
        Console.WriteLine("-".PadRight(80, '-'));

        // C# 12: Collection expression syntax
        string[] secrets = ["sk-PRODUCTION-SECRET-12345", "backup-key-67890"];
        
        // Bypass: Direct array access
        Console.WriteLine($"✗ BYPASSED (Array Access): {secrets[0]}");
        
        // Bypass 2: Iterate collection
        foreach (var secret in secrets)
        {
            Console.WriteLine($"✗ BYPASSED (Iteration): {secret}");
            break; // Just show first one
        }
        
        Console.WriteLine("  Attack: Collection expressions don't provide security");
        Console.WriteLine();
    }

    // ========================================================================
    // ATTEMPT 7: ref readonly Parameters (C# 12)
    // ========================================================================
    static void Attempt7_RefReadonlyParameters()
    {
        Console.WriteLine("ATTEMPT 7: ref readonly Parameters (C# 12 Feature)");
        Console.WriteLine("-".PadRight(80, '-'));

        var secret = new SecretData { Value = "sk-PRODUCTION-SECRET-12345" };
        ProcessSecret(in secret);
        
        // Bypass: ref readonly doesn't prevent reading
        Console.WriteLine($"✗ BYPASSED (Direct Access): {secret.Value}");
        Console.WriteLine("  Attack: ref readonly prevents modification, not inspection");
        Console.WriteLine();
    }

    struct SecretData
    {
        public string Value { get; set; }
    }

    static void ProcessSecret(ref readonly SecretData secret)
    {
        // Can read, cannot modify
        Console.WriteLine($"✗ BYPASSED (ref readonly): {secret.Value}");
    }

    // ========================================================================
    // ATTEMPT 8: Unsafe Pointers (Low-Level Memory)
    // ========================================================================
    static unsafe void Attempt8_UnsafePointers()
    {
        Console.WriteLine("ATTEMPT 8: Unsafe Pointers for Direct Memory Control");
        Console.WriteLine("-".PadRight(80, '-'));

        string secret = "sk-PRODUCTION-SECRET-12345";
        
        // Even with unsafe pointers, the string is still in managed memory
        fixed (char* ptr = secret)
        {
            // Bypass: Just use the pointer to read it
            var extractedSecret = new string(ptr);
            Console.WriteLine($"✗ BYPASSED (Pointer): {extractedSecret}");
        }
        
        // Bypass 2: Access original string (it's still there)
        Console.WriteLine($"✗ BYPASSED (Direct): {secret}");
        Console.WriteLine("  Attack: Unsafe code doesn't prevent memory access");
        Console.WriteLine("  Note: Strings are immutable and interned");
        Console.WriteLine();
    }

    // ========================================================================
    // ATTEMPT 9: Internal Modifier (Assembly-Level Protection)
    // ========================================================================
    static void Attempt9_InternalModifier()
    {
        Console.WriteLine("ATTEMPT 9: Internal Modifier (Assembly Protection)");
        Console.WriteLine("-".PadRight(80, '-'));

        var holder = new InternalSecret("sk-PRODUCTION-SECRET-12345");
        
        // Bypass: Reflection ignores internal modifier
        var fieldInfo = typeof(InternalSecret).GetField("_apiKey",
            BindingFlags.NonPublic | BindingFlags.Instance);
        var extractedSecret = (string)fieldInfo.GetValue(holder);
        
        Console.WriteLine($"✗ BYPASSED (Reflection): {extractedSecret}");
        Console.WriteLine("  Attack: internal only prevents compile-time access");
        Console.WriteLine();
    }

    internal class InternalSecret
    {
        private readonly string _apiKey;
        
        internal InternalSecret(string apiKey)
        {
            _apiKey = apiKey;
        }
    }

    // ========================================================================
    // ATTEMPT 10: Interceptors (C# 12 Preview)
    // ========================================================================
    static void Attempt10_Interceptors()
    {
        Console.WriteLine("ATTEMPT 10: Interceptors (C# 12 Preview Feature)");
        Console.WriteLine("-".PadRight(80, '-'));

        // Note: Interceptors are compile-time feature for source generators
        // They don't provide runtime security
        var secret = GetInterceptableSecret();
        
        Console.WriteLine($"✗ BYPASSED (Direct Call): {secret}");
        Console.WriteLine("  Attack: Interceptors are compile-time only");
        Console.WriteLine("  Note: Source generators don't protect runtime data");
        Console.WriteLine();
    }

    static string GetInterceptableSecret()
    {
        return "sk-PRODUCTION-SECRET-12345";
    }

    // ========================================================================
    // SUMMARY
    // ========================================================================
    static void PrintSummary()
    {
        Console.WriteLine("=".PadRight(80, '='));
        Console.WriteLine("RESULTS: ALL 10 PROTECTION MECHANISMS WERE BYPASSED");
        Console.WriteLine("=".PadRight(80, '='));
        Console.WriteLine();
        Console.WriteLine("Why C# 12 (.NET 8) Cannot Provide Absolute Security:");
        Console.WriteLine("  1. Reflection API: Complete runtime introspection");
        Console.WriteLine("  2. Marshal Class: Direct memory access and manipulation");
        Console.WriteLine("  3. Unsafe Code: Pointer arithmetic bypasses managed safety");
        Console.WriteLine("  4. Access Modifiers: Only enforce compile-time restrictions");
        Console.WriteLine("  5. SecureString Flaw: Must convert to string for use");
        Console.WriteLine("  6. IL Inspection: All code and constants visible in bytecode");
        Console.WriteLine("  7. C# 12 Features: Primary constructors, collection expressions don't add security");
        Console.WriteLine();
        Console.WriteLine("Attack Vectors Available in C# 12:");
        Console.WriteLine("  ✗ Reflection (FieldInfo.GetValue/SetValue)");
        Console.WriteLine("  ✗ Marshal.SecureStringToBSTR");
        Console.WriteLine("  ✗ Marshal.PtrToStringBSTR");
        Console.WriteLine("  ✗ Unsafe pointers and fixed statements");
        Console.WriteLine("  ✗ BindingFlags bypass all access modifiers");
        Console.WriteLine("  ✗ Auto-property backing field access");
        Console.WriteLine("  ✗ Primary constructor parameter captures");
        Console.WriteLine("  ✗ IL disassembly (ILSpy/dnSpy)");
        Console.WriteLine("  ✗ Debugger attachment");
        Console.WriteLine();
        Console.WriteLine("Protection Success Rate: 0/10 (0%)");
        Console.WriteLine();
        Console.WriteLine("=".PadRight(80, '='));
        Console.WriteLine("CONCLUSION: Absolute secret protection is ARCHITECTURALLY IMPOSSIBLE");
        Console.WriteLine("in C# 12 due to reflection, marshaling, and unsafe memory access.");
        Console.WriteLine("Modern C# 12 features (primary constructors, collection expressions,");
        Console.WriteLine("ref readonly) do not change this fundamental limitation.");
        Console.WriteLine("=".PadRight(80, '='));
        Console.WriteLine();
        Console.WriteLine("See: TARLCSharpProtection.cs for how T.A.R.L. solves this");
    }
}
