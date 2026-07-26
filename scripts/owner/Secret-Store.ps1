Set-StrictMode -Version Latest

function Get-OwnerRepositoryRoot {
    return [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot "..\.."))
}

function Get-OwnerStateRoot {
    return Join-Path (Get-OwnerRepositoryRoot) ".owner-state"
}

function Get-OwnerRuntimeRoot {
    if (-not [Runtime.InteropServices.RuntimeInformation]::IsOSPlatform(
        [Runtime.InteropServices.OSPlatform]::Windows
    )) {
        return Join-Path (Get-OwnerStateRoot) "runtime"
    }
    $identity = [Security.Principal.WindowsIdentity]::GetCurrent().User
    if ($null -eq $identity) {
        throw "Could not resolve the current Windows identity for runtime secrets."
    }
    $commonData = [Environment]::GetFolderPath(
        [Environment+SpecialFolder]::CommonApplicationData
    )
    if (-not $commonData) {
        throw "Could not resolve the Windows common application-data directory."
    }
    return Join-Path $commonData "Project-AI\owner-runtime\$($identity.Value)"
}

function ConvertTo-PlainText {
    param([Parameter(Mandatory = $true)][SecureString]$Value)

    $pointer = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($Value)
    try {
        return [Runtime.InteropServices.Marshal]::PtrToStringBSTR($pointer)
    }
    finally {
        [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($pointer)
    }
}

function New-OwnerRandomSecret {
    param(
        [int]$Bytes = 48,
        [switch]$Fernet
    )

    $buffer = [byte[]]::new($Bytes)
    [Security.Cryptography.RandomNumberGenerator]::Fill($buffer)
    $value = [Convert]::ToBase64String($buffer)
    if ($Fernet) {
        return $value.Replace("+", "-").Replace("/", "_")
    }
    return $value
}

function Get-OwnerPortableKey {
    param(
        [Parameter(Mandatory = $true)][SecureString]$Passphrase,
        [Parameter(Mandatory = $true)][byte[]]$Salt
    )

    $plain = ConvertTo-PlainText -Value $Passphrase
    try {
        $derive = [Security.Cryptography.Rfc2898DeriveBytes]::new(
            $plain,
            $Salt,
            200000,
            [Security.Cryptography.HashAlgorithmName]::SHA256
        )
        try {
            return $derive.GetBytes(32)
        }
        finally {
            $derive.Dispose()
        }
    }
    finally {
        $plain = $null
    }
}

function Set-OwnerRestrictedAcl {
    param([Parameter(Mandatory = $true)][string]$LiteralPath)

    if (-not [Runtime.InteropServices.RuntimeInformation]::IsOSPlatform(
        [Runtime.InteropServices.OSPlatform]::Windows
    )) {
        return
    }
    $identity = [Security.Principal.WindowsIdentity]::GetCurrent().User
    if ($null -eq $identity) {
        throw "Could not resolve the current Windows identity for secret-store ACLs."
    }
    $item = Get-Item -LiteralPath $LiteralPath
    if ($item.PSIsContainer) {
        $grant = "*$($identity.Value):(OI)(CI)F"
    }
    else {
        $grant = "*$($identity.Value):F"
    }
    & icacls.exe $LiteralPath /inheritance:r /grant:r $grant *> $null
    if ($LASTEXITCODE -ne 0) {
        throw "Could not restrict access to owner secret path: $LiteralPath"
    }
}

function Set-OwnerDockerRuntimeAcl {
    param([Parameter(Mandatory = $true)][string]$LiteralPath)

    if (-not [Runtime.InteropServices.RuntimeInformation]::IsOSPlatform(
        [Runtime.InteropServices.OSPlatform]::Windows
    )) {
        Set-OwnerRestrictedAcl -LiteralPath $LiteralPath
        return
    }
    $identity = [Security.Principal.WindowsIdentity]::GetCurrent().User
    if ($null -eq $identity) {
        throw "Could not resolve the current Windows identity for runtime-secret ACLs."
    }
    try {
        $dockerUsers = [Security.Principal.NTAccount]::new(
            "$env:COMPUTERNAME",
            "docker-users"
        ).Translate([Security.Principal.SecurityIdentifier])
    }
    catch {
        throw "Could not resolve the local docker-users group for runtime-secret ACLs."
    }
    $item = Get-Item -LiteralPath $LiteralPath
    if ($item.PSIsContainer) {
        $ownerGrant = "*$($identity.Value):(OI)(CI)F"
        $dockerGrant = "*$($dockerUsers.Value):(OI)(CI)RX"
        $systemGrant = "*S-1-5-18:(OI)(CI)F"
        $administratorsGrant = "*S-1-5-32-544:(OI)(CI)F"
    }
    else {
        $ownerGrant = "*$($identity.Value):F"
        $dockerGrant = "*$($dockerUsers.Value):R"
        $systemGrant = "*S-1-5-18:F"
        $administratorsGrant = "*S-1-5-32-544:F"
    }
    & icacls.exe $LiteralPath /inheritance:r /grant:r `
        $ownerGrant $dockerGrant $systemGrant $administratorsGrant *> $null
    if ($LASTEXITCODE -ne 0) {
        throw "Could not grant Docker Desktop access to runtime secret path: $LiteralPath"
    }
}

function Set-OwnerSecret {
    param(
        [Parameter(Mandatory = $true)][string]$Name,
        [Parameter(Mandatory = $true)][string]$Value,
        [SecureString]$PortablePassphrase
    )

    $credentialRoot = Join-Path (Get-OwnerStateRoot) "credentials"
    New-Item -ItemType Directory -Path $credentialRoot -Force | Out-Null
    Set-OwnerRestrictedAcl -LiteralPath $credentialRoot

    $secure = ConvertTo-SecureString -String $Value -AsPlainText -Force
    if ($null -eq $PortablePassphrase) {
        $record = [ordered]@{
            version = 1
            mode = "dpapi-current-user"
            payload = ConvertFrom-SecureString -SecureString $secure
        }
    }
    else {
        $salt = [byte[]]::new(16)
        [Security.Cryptography.RandomNumberGenerator]::Fill($salt)
        $key = Get-OwnerPortableKey -Passphrase $PortablePassphrase -Salt $salt
        try {
            $record = [ordered]@{
                version = 1
                mode = "portable-passphrase"
                salt = [Convert]::ToBase64String($salt)
                payload = ConvertFrom-SecureString -SecureString $secure -Key $key
            }
        }
        finally {
            [Array]::Clear($key, 0, $key.Length)
        }
    }

    $path = Join-Path $credentialRoot "$Name.json"
    $json = $record | ConvertTo-Json -Depth 4
    [IO.File]::WriteAllText($path, $json, [Text.UTF8Encoding]::new($false))
    Set-OwnerRestrictedAcl -LiteralPath $path
}

function Get-OwnerSecret {
    param(
        [Parameter(Mandatory = $true)][string]$Name,
        [SecureString]$PortablePassphrase
    )

    $path = Join-Path (Join-Path (Get-OwnerStateRoot) "credentials") "$Name.json"
    if (-not (Test-Path -LiteralPath $path)) {
        throw "Owner credential '$Name' is missing. Run the owner start path to initialize it."
    }
    $record = Get-Content -LiteralPath $path -Raw | ConvertFrom-Json
    if ($record.version -ne 1) {
        throw "Owner credential '$Name' has an unsupported record version."
    }
    if ($record.mode -eq "dpapi-current-user") {
        $secure = ConvertTo-SecureString -String $record.payload
    }
    elseif ($record.mode -eq "portable-passphrase") {
        if ($null -eq $PortablePassphrase) {
            throw "Owner credential '$Name' requires -PortablePassphrase."
        }
        $salt = [Convert]::FromBase64String($record.salt)
        $key = Get-OwnerPortableKey -Passphrase $PortablePassphrase -Salt $salt
        try {
            $secure = ConvertTo-SecureString -String $record.payload -Key $key
        }
        finally {
            [Array]::Clear($key, 0, $key.Length)
        }
    }
    else {
        throw "Owner credential '$Name' has an unsupported protection mode."
    }
    return ConvertTo-PlainText -Value $secure
}

function Initialize-OwnerSecretStore {
    param([SecureString]$PortablePassphrase)

    $definitions = @(
        @{ Name = "setup-secret"; Fernet = $false; Bytes = 48 },
        @{ Name = "mfa-key"; Fernet = $true; Bytes = 32 },
        @{ Name = "execution-secret"; Fernet = $false; Bytes = 48 },
        @{ Name = "postgres-password"; Fernet = $false; Bytes = 48 }
    )
    $created = [System.Collections.Generic.List[string]]::new()
    foreach ($definition in $definitions) {
        $path = Join-Path (Join-Path (Get-OwnerStateRoot) "credentials") "$($definition.Name).json"
        if (Test-Path -LiteralPath $path) {
            continue
        }
        $value = New-OwnerRandomSecret -Bytes $definition.Bytes -Fernet:$definition.Fernet
        Set-OwnerSecret -Name $definition.Name -Value $value -PortablePassphrase $PortablePassphrase
        $created.Add($definition.Name)
        $value = $null
    }
    return $created.ToArray()
}

function Write-OwnerRuntimeSecrets {
    param([SecureString]$PortablePassphrase)

    $runtimeRoot = Get-OwnerRuntimeRoot
    $resolvedRuntime = [IO.Path]::GetFullPath($runtimeRoot)
    if ([Runtime.InteropServices.RuntimeInformation]::IsOSPlatform(
        [Runtime.InteropServices.OSPlatform]::Windows
    )) {
        $commonData = [IO.Path]::GetFullPath(
            [Environment]::GetFolderPath(
                [Environment+SpecialFolder]::CommonApplicationData
            )
        )
        $runtimeBase = [IO.Path]::GetFullPath(
            (Join-Path $commonData "Project-AI\owner-runtime")
        )
        if (-not $resolvedRuntime.StartsWith(
            $runtimeBase,
            [StringComparison]::OrdinalIgnoreCase
        )) {
            throw "Refusing to prepare a runtime secret path outside Project-AI common data."
        }
    }
    else {
        $resolvedState = [IO.Path]::GetFullPath((Get-OwnerStateRoot))
        if (-not $resolvedRuntime.StartsWith(
            $resolvedState,
            [StringComparison]::OrdinalIgnoreCase
        )) {
            throw "Refusing to prepare a runtime secret path outside .owner-state."
        }
    }
    if (Test-Path -LiteralPath $runtimeRoot) {
        Remove-Item -LiteralPath $runtimeRoot -Recurse -Force
    }
    New-Item -ItemType Directory -Path $runtimeRoot -Force | Out-Null
    Set-OwnerDockerRuntimeAcl -LiteralPath $runtimeRoot

    $values = @{
        "setup-secret" = Get-OwnerSecret -Name "setup-secret" -PortablePassphrase $PortablePassphrase
        "mfa-key" = Get-OwnerSecret -Name "mfa-key" -PortablePassphrase $PortablePassphrase
        "execution-secret" = Get-OwnerSecret -Name "execution-secret" -PortablePassphrase $PortablePassphrase
        "postgres-password" = Get-OwnerSecret -Name "postgres-password" -PortablePassphrase $PortablePassphrase
    }
    $escapedPassword = [Uri]::EscapeDataString($values["postgres-password"])
    $values["database-url"] = "postgresql://project_ai:$escapedPassword@postgres:5432/project_ai"

    foreach ($entry in $values.GetEnumerator()) {
        $path = Join-Path $runtimeRoot $entry.Key
        [IO.File]::WriteAllText($path, $entry.Value, [Text.UTF8Encoding]::new($false))
        Set-OwnerDockerRuntimeAcl -LiteralPath $path
    }
    $env:PROJECT_AI_RUNTIME_SECRET_ROOT = $resolvedRuntime
    return $runtimeRoot
}

function Remove-OwnerRuntimeSecrets {
    $runtimeRoot = [IO.Path]::GetFullPath((Get-OwnerRuntimeRoot))
    if ([Runtime.InteropServices.RuntimeInformation]::IsOSPlatform(
        [Runtime.InteropServices.OSPlatform]::Windows
    )) {
        $runtimeBase = [IO.Path]::GetFullPath(
            (Join-Path (
                [Environment]::GetFolderPath(
                    [Environment+SpecialFolder]::CommonApplicationData
                )
            ) "Project-AI\owner-runtime")
        )
        if (-not $runtimeRoot.StartsWith(
            $runtimeBase,
            [StringComparison]::OrdinalIgnoreCase
        )) {
            throw "Refusing to remove a runtime secret path outside Project-AI common data."
        }
    }
    else {
        $stateRoot = [IO.Path]::GetFullPath((Get-OwnerStateRoot))
        if (-not $runtimeRoot.StartsWith(
            $stateRoot,
            [StringComparison]::OrdinalIgnoreCase
        )) {
            throw "Refusing to remove a runtime secret path outside .owner-state."
        }
    }
    if (Test-Path -LiteralPath $runtimeRoot) {
        Remove-Item -LiteralPath $runtimeRoot -Recurse -Force
    }
}

function Protect-OwnerArchive {
    param(
        [Parameter(Mandatory = $true)][string]$InputPath,
        [Parameter(Mandatory = $true)][string]$OutputPath,
        [SecureString]$PortablePassphrase
    )

    $plain = [IO.File]::ReadAllBytes($InputPath)
    $magic = [Text.Encoding]::ASCII.GetBytes("PAIBKP01")
    if ($null -eq $PortablePassphrase) {
        $protected = [Security.Cryptography.ProtectedData]::Protect(
            $plain,
            $magic,
            [Security.Cryptography.DataProtectionScope]::CurrentUser
        )
        $payload = [byte[]]::new($magic.Length + 1 + $protected.Length)
        [Array]::Copy($magic, 0, $payload, 0, $magic.Length)
        $payload[$magic.Length] = 1
        [Array]::Copy($protected, 0, $payload, $magic.Length + 1, $protected.Length)
    }
    else {
        $salt = [byte[]]::new(16)
        $nonce = [byte[]]::new(12)
        $tag = [byte[]]::new(16)
        [Security.Cryptography.RandomNumberGenerator]::Fill($salt)
        [Security.Cryptography.RandomNumberGenerator]::Fill($nonce)
        $key = Get-OwnerPortableKey -Passphrase $PortablePassphrase -Salt $salt
        $cipher = [byte[]]::new($plain.Length)
        try {
            $aes = [Security.Cryptography.AesGcm]::new($key, 16)
            try {
                $aes.Encrypt($nonce, $plain, $cipher, $tag, $magic)
            }
            finally {
                $aes.Dispose()
            }
        }
        finally {
            [Array]::Clear($key, 0, $key.Length)
        }
        $payload = [byte[]]::new($magic.Length + 1 + 16 + 12 + 16 + $cipher.Length)
        $offset = 0
        foreach ($part in @($magic, [byte[]]@(2), $salt, $nonce, $tag, $cipher)) {
            [Array]::Copy($part, 0, $payload, $offset, $part.Length)
            $offset += $part.Length
        }
    }
    [IO.File]::WriteAllBytes($OutputPath, $payload)
    [Array]::Clear($plain, 0, $plain.Length)
}

function Unprotect-OwnerArchive {
    param(
        [Parameter(Mandatory = $true)][string]$InputPath,
        [Parameter(Mandatory = $true)][string]$OutputPath,
        [SecureString]$PortablePassphrase
    )

    $payload = [IO.File]::ReadAllBytes($InputPath)
    $magic = [Text.Encoding]::ASCII.GetBytes("PAIBKP01")
    if ($payload.Length -lt 10) {
        throw "Backup archive is truncated."
    }
    for ($index = 0; $index -lt $magic.Length; $index++) {
        if ($payload[$index] -ne $magic[$index]) {
            throw "Backup archive header is invalid."
        }
    }
    $mode = $payload[$magic.Length]
    if ($mode -eq 1) {
        $protected = $payload[($magic.Length + 1)..($payload.Length - 1)]
        $plain = [Security.Cryptography.ProtectedData]::Unprotect(
            $protected,
            $magic,
            [Security.Cryptography.DataProtectionScope]::CurrentUser
        )
    }
    elseif ($mode -eq 2) {
        if ($null -eq $PortablePassphrase) {
            throw "This backup requires -PortablePassphrase."
        }
        $offset = $magic.Length + 1
        $salt = $payload[$offset..($offset + 15)]
        $offset += 16
        $nonce = $payload[$offset..($offset + 11)]
        $offset += 12
        $tag = $payload[$offset..($offset + 15)]
        $offset += 16
        $cipher = $payload[$offset..($payload.Length - 1)]
        $plain = [byte[]]::new($cipher.Length)
        $key = Get-OwnerPortableKey -Passphrase $PortablePassphrase -Salt $salt
        try {
            $aes = [Security.Cryptography.AesGcm]::new($key, 16)
            try {
                $aes.Decrypt($nonce, $cipher, $tag, $plain, $magic)
            }
            finally {
                $aes.Dispose()
            }
        }
        finally {
            [Array]::Clear($key, 0, $key.Length)
        }
    }
    else {
        throw "Backup archive protection mode is unsupported."
    }
    [IO.File]::WriteAllBytes($OutputPath, $plain)
    [Array]::Clear($plain, 0, $plain.Length)
}
