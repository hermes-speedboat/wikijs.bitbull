---
title: Purge M365 Mailbox
description: Step by step instructions how to permanently delete a m365 mailbox
published: true
date: 2026-06-02T10:40:57.302Z
tags: windows, 365
editor: markdown
dateCreated: 2026-06-02T10:40:57.302Z
---

# Cleanly delete and recreate a Microsoft 365 test mailbox

Goal: For migration testing, an Exchange Online mailbox should be fully removed so that the next AD sync / license assignment creates a new empty mailbox instead of reconnecting the old soft-deleted mailbox.

> Warning: `Remove-Mailbox -PermanentlyDelete` deletes mailbox data irreversibly. Use this only for test mailboxes. Before deleting, check for Litigation Hold, eDiscovery Hold, retention/Purview holds, delay holds, or inactive mailbox state. Do not remove holds casually if compliance/legal retention may apply.

## Prerequisites

- The user is synchronized from on-premises Active Directory.
- Access to the Microsoft Entra Connect / Azure AD Connect server, for example `AzureConnector`.
- PowerShell with administrative permissions.
- Exchange Online Management module on the admin VM.
- Tenant permissions:
  - Exchange Administrator or higher for Exchange Online PowerShell.
  - User Administrator / Global Administrator for deleted Entra users.
- Affected test user, example:
  - `user@domain.tld`
  - On-prem AD attribute: `extensionAttribute1`, or whichever attribute controls synchronization / mailbox provisioning in your environment.

## Short explanation of the Microsoft behavior

- If a synchronized user is taken out of scope, the cloud user usually moves to **Deleted users** in Entra ID.
- The Exchange Online mailbox usually becomes a **soft-deleted mailbox**.
- As long as the soft-deleted mailbox still exists, Exchange Online may reconnect it when the user is synchronized again.
- To force creation of a new empty mailbox, the soft-deleted mailbox must be permanently deleted.

## Process overview

1. Document the current user and mailbox state.
2. Clear on-prem `extensionAttribute1`.
3. Start a delta sync on the AzureConnector server.
4. Wait until the user is no longer visible as an active user in Microsoft 365 / Entra ID.
5. Permanently delete the user from **Deleted users** in Entra ID.
6. Check Exchange Online for a soft-deleted mailbox.
7. Permanently delete the soft-deleted mailbox.
8. Verify that no soft-deleted mailbox remains.
9. Set on-prem `extensionAttribute1` again.
10. Start another delta sync on the AzureConnector server.
11. Verify license assignment and mailbox provisioning. A new mailbox should be created.

---

## 1. Document the current state first

On an admin system with the Active Directory PowerShell module:

```powershell
$userSam = "USERNAME"                 # Example: m.muster
$userUpn = "user@domain.tld"

Get-ADUser $userSam -Properties userPrincipalName,mail,proxyAddresses,extensionAttribute1,msExchMailboxGuid,msExchArchiveGuid |
  Format-List Name,SamAccountName,UserPrincipalName,mail,extensionAttribute1,msExchMailboxGuid,msExchArchiveGuid,proxyAddresses
```

Optional backup export:

```powershell
Get-ADUser $userSam -Properties * |
  Export-Clixml ".\$userSam-before-mailbox-reset.xml"
```

## 2. Clear `extensionAttribute1` in on-prem AD

Option A: PowerShell:

```powershell
$userSam = "USERNAME"

Set-ADUser $userSam -Clear extensionAttribute1

Get-ADUser $userSam -Properties extensionAttribute1 |
  Select-Object SamAccountName,extensionAttribute1
```

Option B: ADUC / Attribute Editor:

- Open the user object.
- Open **Attribute Editor**.
- Clear `extensionAttribute1`.
- Save the change.

## 3. Start a delta sync on AzureConnector

On the Microsoft Entra Connect / Azure AD Connect server, run PowerShell as administrator:

```powershell
Import-Module ADSync
Get-ADSyncScheduler
Start-ADSyncSyncCycle -PolicyType Delta
```

Check sync status:

```powershell
Get-ADSyncScheduler | Format-List SyncCycleInProgress,NextSyncCycleStartTimeInUTC,NextSyncCyclePolicyType
```

If `Start-ADSyncSyncCycle` is not available, make sure you are really on the Entra Connect server and that `Import-Module ADSync` works.

## 4. Wait and verify that the cloud user is no longer active

Portal checks:

- Microsoft 365 Admin Center: **Users** > **Active users**
- Entra Admin Center: **Entra ID** > **Users** > **All users**

After a successful sync, the user should no longer be visible as an active user.

Optional Microsoft Graph PowerShell check:

```powershell
Connect-MgGraph -Scopes "User.Read.All","Directory.Read.All"
Get-MgUser -UserId "user@domain.tld" -ErrorAction SilentlyContinue
```

If the user is still active:

- Wait until the sync has completed.
- Verify that the on-prem attribute was actually cleared.
- Check whether another sync rule still keeps the user in scope.

## 5. Permanently delete the Entra deleted user

In the Entra Admin Center:

- Go to **Entra ID** > **Users** > **Deleted users**.
- Search for the user.
- Select the user.
- Run **Delete permanently**.

Alternative via Microsoft Graph PowerShell:

```powershell
Connect-MgGraph -Scopes "User.DeleteRestore.All","Directory.AccessAsUser.All"

$userUpn = "user@domain.tld"
$deletedUser = Get-MgDirectoryDeletedItemAsUser -Filter "userPrincipalName eq '$userUpn'"

$deletedUser | Format-List Id,DisplayName,UserPrincipalName,DeletedDateTime

Remove-MgDirectoryDeletedItem -DirectoryObjectId $deletedUser.Id
```

Important: A permanently deleted Entra user cannot be restored. In this procedure, that is intentional because the user will later be synchronized again from on-prem AD.

## 6. Connect to Exchange Online

On the PowerShell admin VM:

```powershell
Install-Module ExchangeOnlineManagement -Scope CurrentUser
Import-Module ExchangeOnlineManagement
Connect-ExchangeOnline
```

If the module is already installed:

```powershell
Import-Module ExchangeOnlineManagement
Connect-ExchangeOnline
```

## 7. Check for the soft-deleted mailbox

```powershell
$userUpn = "user@domain.tld"

Get-Mailbox -Identity $userUpn -SoftDeletedMailbox | Format-List `
  DisplayName,UserPrincipalName,PrimarySmtpAddress,ExchangeGuid,Guid,WhenSoftDeleted, `
  LitigationHoldEnabled,InPlaceHolds,RetentionHoldEnabled,DelayHoldApplied,DelayReleaseHoldApplied,IsInactiveMailbox
```

Interpretation:

- No result: There is no soft-deleted mailbox left. Continue with step 9.
- Result without holds: The mailbox can be permanently deleted for the test scenario.
- Result with holds or `IsInactiveMailbox = True`: Do not simply delete it. Check compliance/retention requirements first.

## 8. Permanently delete the soft-deleted mailbox

Only run this if you are sure that it is a test mailbox and no relevant holds apply:

```powershell
$userUpn = "user@domain.tld"

Get-Mailbox -Identity $userUpn -SoftDeletedMailbox |
  Remove-Mailbox -PermanentlyDelete -Confirm:$false
```

Verify afterwards:

```powershell
Get-Mailbox -Identity $userUpn -SoftDeletedMailbox
```

Expected result: object not found / no output.

Optional search across all soft-deleted mailboxes:

```powershell
Get-Mailbox -SoftDeletedMailbox -ResultSize Unlimited |
  Where-Object {$_.PrimarySmtpAddress -eq "user@domain.tld" -or $_.UserPrincipalName -eq "user@domain.tld"} |
  Format-List DisplayName,UserPrincipalName,PrimarySmtpAddress,ExchangeGuid,WhenSoftDeleted
```

## 9. Set `extensionAttribute1` again in on-prem AD

Use the correct value from your documentation / provisioning concept:

```powershell
$userSam = "USERNAME"
$value = "CORRECT-VALUE"

Set-ADUser $userSam -Replace @{extensionAttribute1=$value}

Get-ADUser $userSam -Properties extensionAttribute1 |
  Select-Object SamAccountName,extensionAttribute1
```

## 10. Start another delta sync

On the AzureConnector server:

```powershell
Import-Module ADSync
Start-ADSyncSyncCycle -PolicyType Delta
```

Wait until the sync has completed.

## 11. Verify that the user and mailbox were recreated

Entra / Microsoft 365 Admin Center:

- The user appears again under active users.
- The Exchange Online license is assigned correctly, either directly or through group-based licensing.

Exchange Online:

```powershell
$userUpn = "user@domain.tld"

Get-EXOMailbox -Identity $userUpn | Format-List DisplayName,UserPrincipalName,PrimarySmtpAddress,ExchangeGuid,WhenCreated
```

If no mailbox exists:

- Check license assignment.
- Check whether the Exchange Online service plan is enabled.
- Wait a few minutes; mailbox provisioning can take some time.
- Check again.

## Troubleshooting

### User does not disappear from Entra ID

- `extensionAttribute1` may not be the only scoping criterion.
- Entra Connect sync did not run or failed.
- Check sync rules, OU filtering, and attribute filtering.
- Check Synchronization Service Manager on the AzureConnector server.

### User remains under Deleted users

- Permanently delete the user in the Entra Admin Center.
- For on-prem synced users, make sure the user is not immediately synchronized again while `extensionAttribute1` is still empty.

### Soft-deleted mailbox cannot be deleted

Common causes:

- Litigation Hold is enabled.
- eDiscovery / Purview retention hold is active.
- The mailbox is an inactive mailbox.
- `DelayHoldApplied` / `DelayReleaseHoldApplied` is active.

Do not simply remove holds. Clarify the compliance/retention concept first.

### The old mailbox comes back after resync

The soft-deleted mailbox was probably not permanently deleted, or Exchange reconnected it based on `ExchangeGuid` / `ArchiveGuid`. Check:

```powershell
Get-Mailbox -SoftDeletedMailbox -ResultSize Unlimited |
  Where-Object {$_.UserPrincipalName -like "*user@domain.tld*" -or $_.PrimarySmtpAddress -eq "user@domain.tld"} |
  Format-List DisplayName,UserPrincipalName,PrimarySmtpAddress,ExchangeGuid,ArchiveGuid,WhenSoftDeleted
```

## References

- Microsoft Learn: Delete or restore user mailboxes in Exchange Online  
  https://learn.microsoft.com/en-us/exchange/recipients-in-exchange-online/delete-or-restore-mailboxes
- Microsoft Learn: Microsoft Entra Connect Sync Scheduler  
  https://learn.microsoft.com/en-us/entra/identity/hybrid/connect/how-to-connect-sync-feature-scheduler
- Microsoft Learn: Restore or permanently remove recently deleted users  
  https://learn.microsoft.com/en-us/entra/fundamentals/users-restore
