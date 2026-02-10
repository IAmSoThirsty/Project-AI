/*
 * C# Security Demonstration: Why Absolute Secret Protection is IMPOSSIBLE
 * 
 * This demonstrates that C# CANNOT provide absolute protection for secrets,
 * even with best practices, due to fundamental architectural constraints.
 * 
 * The Challenge: Protect an API key so that even with full access to the .NET
 * runtime, an attacker cannot extract it.
 * 
 * Result: IMPOSSIBLE in C# - all protection mechanisms can be bypassed.
 * 
 * Build: csc CSharpImpossibility.cs
 * Run: ./CSharpImpossibility.exe (Windows) or mono CSharpImpossibility.exe (Linux/Mac)
 * Or with .NET Core: dotnet run
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
        Console.WriteLine("=".PadRight(80, '='));
        Console.WriteLine();

        Attempt1_PrivateField();
        Attempt2_ReadonlyField();
        Attempt3_PropertyWithPrivateBackingField();
        Attempt4_SecureString();
        Attempt5_ConstantField();
        Attempt6_StaticConstructor();
        Attempt7_UnsafePointers();
        Attempt8_InternalModifier();

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
    // ATTEMPT 5: Constant Field
    // ========================================================================
    static void Attempt5_ConstantField()
    {
        Console.WriteLine("ATTEMPT 5: Constant Field (Compile-Time)");
        Console.WriteLine("-".PadRight(80, '-'));

        // Bypass: Access via reflection on type
        var fieldInfo = typeof(ConstantSecret).GetField("API_KEY",
            BindingFlags.Public | BindingFlags.Static);
        var extractedSecret = (string)fieldInfo.GetValue(null);
        
        Console.WriteLine($"✗ BYPASSED (Reflection): {extractedSecret}");
        
        // Bypass 2: Direct access (even from outside class if public)
        Console.WriteLine($"✗ BYPASSED (Direct): {ConstantSecret.API_KEY}");
        Console.WriteLine("  Attack: Constants are embedded in IL and fully accessible");
        Console.WriteLine();
    }

    class ConstantSecret
    {
        public const string API_KEY = "sk-PRODUCTION-SECRET-12345";
    }

    // ========================================================================
    // ATTEMPT 6: Static Constructor with Closure
    // ========================================================================
    static void Attempt6_StaticConstructor()
    {
        Console.WriteLine("ATTEMPT 6: Static Constructor with Private Storage");
        Console.WriteLine("-".PadRight(80, '-'));

        var secret = StaticConstructorSecret.GetKey();
        Console.WriteLine($"✗ Got secret normally: {secret}");
        
        // Bypass: Access static field via reflection
        var fieldInfo = typeof(StaticConstructorSecret).GetField("_staticApiKey",
            BindingFlags.NonPublic | BindingFlags.Static);
        var extractedSecret = (string)fieldInfo.GetValue(null);
        
        Console.WriteLine($"✗ BYPASSED (Reflection): {extractedSecret}");
        Console.WriteLine("  Attack: Static fields are still accessible via reflection");
        Console.WriteLine();
    }

    class StaticConstructorSecret
    {
        private static readonly string _staticApiKey;
        
        static StaticConstructorSecret()
        {
            _staticApiKey = "sk-PRODUCTION-SECRET-12345";
        }
        
        public static string GetKey() => _staticApiKey;
    }

    // ========================================================================
    // ATTEMPT 7: Unsafe Pointers (Low-Level Memory)
    // ========================================================================
    static unsafe void Attempt7_UnsafePointers()
    {
        Console.WriteLine("ATTEMPT 7: Unsafe Pointers for Direct Memory Control");
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
    // ATTEMPT 8: Internal Modifier (Assembly-Level Protection)
    // ========================================================================
    static void Attempt8_InternalModifier()
    {
        Console.WriteLine("ATTEMPT 8: Internal Modifier (Assembly Protection)");
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
    // SUMMARY
    // ========================================================================
    static void PrintSummary()
    {
        Console.WriteLine("=".PadRight(80, '='));
        Console.WriteLine("RESULTS: ALL 8 PROTECTION MECHANISMS WERE BYPASSED");
        Console.WriteLine("=".PadRight(80, '='));
        Console.WriteLine();
        Console.WriteLine("Why C# Cannot Provide Absolute Security:");
        Console.WriteLine("  1. Reflection API: Complete runtime introspection");
        Console.WriteLine("  2. Marshal Class: Direct memory access and manipulation");
        Console.WriteLine("  3. Unsafe Code: Pointer arithmetic bypasses managed safety");
        Console.WriteLine("  4. Access Modifiers: Only enforce compile-time restrictions");
        Console.WriteLine("  5. SecureString Flaw: Must convert to string for use");
        Console.WriteLine("  6. IL Inspection: All code and constants visible in bytecode");
        Console.WriteLine();
        Console.WriteLine("Attack Vectors Available in C#:");
        Console.WriteLine("  ✗ Reflection (FieldInfo.GetValue/SetValue)");
        Console.WriteLine("  ✗ Marshal.SecureStringToBSTR");
        Console.WriteLine("  ✗ Marshal.PtrToStringBSTR");
        Console.WriteLine("  ✗ Unsafe pointers and fixed statements");
        Console.WriteLine("  ✗ BindingFlags bypass all access modifiers");
        Console.WriteLine("  ✗ Auto-property backing field access");
        Console.WriteLine("  ✗ IL disassembly (ildasm/dnSpy)");
        Console.WriteLine("  ✗ Debugger attachment");
        Console.WriteLine();
        Console.WriteLine("Protection Success Rate: 0/8 (0%)");
        Console.WriteLine();
        Console.WriteLine("=".PadRight(80, '='));
        Console.WriteLine("CONCLUSION: Absolute secret protection is ARCHITECTURALLY IMPOSSIBLE");
        Console.WriteLine("in C# due to reflection, marshaling, and unsafe memory access.");
        Console.WriteLine("=".PadRight(80, '='));
        Console.WriteLine();
        Console.WriteLine("T.A.R.L. Adapter: tarl/adapters/csharp/TARL.cs");
    }
}
