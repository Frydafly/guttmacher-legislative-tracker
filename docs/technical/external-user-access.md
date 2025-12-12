# Granting BigQuery Access to External Users

## Overview

This guide explains how to grant BigQuery access to external collaborators who use **non-Google email addresses** (like `person@organization.com`, `user@outlook.com`, etc.).

!!! success "Good News: It's Simple!"
    You don't need complex enterprise setup. External users can access BigQuery using their existing email address by creating a free Google Account.

---

## Who Needs This Guide?

**Administrators:** You're granting BigQuery access to external users

**External Users:** You need to access Guttmacher's BigQuery data but don't have a Google/Gmail account

---

## Two Methods

=== "Method 1: Google Account (RECOMMENDED)"

    **Best for:** Most use cases - individual users, small teams

    **Time:** 10-15 minutes total

    **Cost:** FREE

    **What it does:** Users create a Google Account using their existing email, you grant them access

    **When to use:** Default choice for 99% of situations

=== "Method 2: Workforce Identity Federation (ADVANCED)"

    **Best for:** Large organizations (100+ users) with existing identity provider (Okta, Azure AD, etc.)

    **Time:** Several hours to configure

    **Cost:** May require enterprise Google Cloud setup

    **What it does:** Enables SSO through your organization's identity provider

    **When to use:** Only if you have IT team and need enterprise SSO

!!! tip "Start with Method 1"
    Unless you have a specific enterprise SSO requirement, use **Method 1**. It's simple, free, and works immediately.

---

## Method 1: Google Account with Existing Email (RECOMMENDED)

### Step-by-Step Process

This process has two parts:
1. **User creates Google Account** using their existing email
2. **Administrator grants BigQuery access** to that account

---

### Part A: User Creates Google Account

The external user needs to create a Google Account using their existing email address (they don't need to create a Gmail account).

#### User Instructions:

**1. Go to Google Account signup page:**

Visit: [accounts.google.com/signup](https://accounts.google.com/signup)

**2. Start account creation:**

- Click "Create account" → "For my personal use"
- Enter first and last name

**3. Use existing email instead of creating Gmail:**

- When asked for username, click **"Use your existing email instead"**
- Enter your work or personal email (e.g., `user@guttmacher.org`)

**4. Create password:**

- Choose a strong password for your Google Account
- This is separate from your email password

**5. Verify email:**

- Google sends verification code to your email
- Enter the code to confirm ownership

**6. Complete setup:**

- Add phone number (optional but recommended for recovery)
- Accept terms of service
- Done!

!!! example "What Users Get"
    After creating the account, users can:

    - Access BigQuery Console with their existing email
    - Use all Google Cloud services
    - Keep their existing email provider (no Gmail required)
    - Sign in to Google using `user@guttmacher.org` instead of `user@gmail.com`

**Video walkthrough:** [How to create Google Account with existing email](https://support.google.com/accounts/answer/27441)

---

### Part B: Administrator Grants BigQuery Access

Once the user has created their Google Account, you can grant them access to BigQuery.

#### Option 1: Using Google Cloud Console (GUI)

**1. Open IAM page:**

1. Go to [console.cloud.google.com/iam-admin/iam](https://console.cloud.google.com/iam-admin/iam)
2. Select project: `guttmacher-legislative-tracker`

**2. Grant access:**

1. Click **"+ Grant Access"** button
2. In "New principals" field, enter user's email: `person@organization.com`
3. Click "Select a role" dropdown

**3. Choose appropriate role:**

=== "Data Viewer (Read-Only)"

    **Role:** `BigQuery Data Viewer`

    **Permissions:**

    - ✅ Run queries
    - ✅ View tables and datasets
    - ✅ Export query results
    - ❌ Cannot create/modify tables
    - ❌ Cannot delete data

    **Best for:** Analysts, researchers, external partners

=== "Job User (Query Runner)"

    **Role:** `BigQuery Job User`

    **Permissions:**

    - ✅ Run queries (required)
    - ❌ Cannot view data without Data Viewer role too

    **Note:** Usually grant BOTH `BigQuery Job User` AND `BigQuery Data Viewer`

=== "Editor (Full Access)"

    **Role:** `BigQuery Data Editor`

    **Permissions:**

    - ✅ Everything in Data Viewer
    - ✅ Create and modify tables
    - ✅ Delete data

    **Best for:** Team members managing the data

**4. Grant the roles:**

For most external users, grant BOTH:

- `BigQuery Job User` (to run queries)
- `BigQuery Data Viewer` (to see data)

Click "Add another role" to assign multiple roles.

**5. Save:**

Click **"Save"**

User now has access! They should receive an email notification.

---

#### Option 2: Using gcloud Command Line

If you prefer command-line tools:

```bash
# Grant BigQuery Data Viewer role
gcloud projects add-iam-policy-binding guttmacher-legislative-tracker \
  --member="user:person@organization.com" \
  --role="roles/bigquery.dataViewer"

# Grant BigQuery Job User role
gcloud projects add-iam-policy-binding guttmacher-legislative-tracker \
  --member="user:person@organization.com" \
  --role="roles/bigquery.jobUser"
```

**For dataset-level access** (instead of project-level):

```bash
# Grant access to specific dataset only
bq show --format=prettyjson guttmacher-legislative-tracker:legislative_tracker_historical > /tmp/dataset.json

# Edit the JSON to add:
{
  "access": [
    {
      "role": "READER",
      "userByEmail": "person@organization.com"
    }
  ]
}

# Apply the updated policy
bq update --source /tmp/dataset.json guttmacher-legislative-tracker:legislative_tracker_historical
```

---

### Part C: User Accesses BigQuery

After access is granted, the external user can access BigQuery:

**1. Go to BigQuery Console:**

Visit: [console.cloud.google.com/bigquery](https://console.cloud.google.com/bigquery)

**2. Sign in:**

- Use the email address with Google Account (e.g., `person@organization.com`)
- Enter the password created in Part A

**3. Access the data:**

In the Explorer panel on left:

1. Click "Add" → "Star a project by name"
2. Enter: `guttmacher-legislative-tracker`
3. Click "Star"

Now the project appears in Explorer:

```
guttmacher-legislative-tracker
  └─ legislative_tracker_historical
      ├─ all_historical_bills_unified
      ├─ comprehensive_bills_authentic
      ├─ looker_bills_dashboard
      └─ ... other tables/views
```

**4. Run a test query:**

Click on any view, then click "Query" button. Try:

```sql
SELECT
  state,
  COUNT(*) as total_bills
FROM `guttmacher-legislative-tracker.legislative_tracker_historical.looker_bills_dashboard`
WHERE data_year = 2024
GROUP BY state
ORDER BY total_bills DESC
LIMIT 10;
```

If this works, access is successfully configured!

---

## Method 2: Workforce Identity Federation (ADVANCED)

!!! warning "Enterprise Feature - Complex Setup"
    Only use this method if you:

    - Have 100+ external users to manage
    - Already use an identity provider (Okta, Azure AD, Google Workspace, etc.)
    - Have IT staff to configure and maintain federation
    - Need enterprise SSO and centralized access control

### What It Does

Workforce Identity Federation lets external users sign in to Google Cloud using their organization's existing identity provider, without creating Google Accounts.

**Flow:**

1. User signs in to their organization's SSO (e.g., Okta)
2. Identity provider authenticates user
3. Google Cloud trusts that authentication
4. User accesses BigQuery without separate Google Account

### When to Use This

**Use Workforce Identity Federation if:**

- ✅ You manage 100+ external users
- ✅ You have Okta, Azure AD, or other SAML/OIDC identity provider
- ✅ You need centralized user management
- ✅ You have IT team to configure federation
- ✅ Compliance requires SSO

**Don't use if:**

- ❌ You have < 20 external users (too much overhead)
- ❌ You don't have existing identity provider
- ❌ You need quick access (this takes hours to set up)

### High-Level Setup

1. **Configure identity provider:**
   - Set up Google Cloud as SAML/OIDC application in your IdP
   - Map user attributes (email, groups, etc.)

2. **Create workforce pool in Google Cloud:**
   - Create workforce identity pool
   - Configure provider settings (SAML or OIDC)
   - Map IdP attributes to Google Cloud identities

3. **Grant access using workforce identities:**
   - Use workforce principal identifiers instead of email addresses
   - Example: `principal://iam.googleapis.com/locations/global/workforcePools/POOL_ID/subject/user@example.com`

4. **Test access:**
   - Users sign in through IdP
   - Access BigQuery via federated identity

### Documentation

This setup is beyond the scope of this guide. Refer to official documentation:

- [Workforce Identity Federation Overview](https://cloud.google.com/iam/docs/workforce-identity-federation)
- [Configuring Workforce Identity Federation](https://cloud.google.com/iam/docs/configuring-workforce-identity-federation)
- [Use case: BigQuery access with Azure AD](https://cloud.google.com/iam/docs/workforce-sign-in-power-bi)

!!! tip "Get Expert Help"
    If you need Workforce Identity Federation, consider hiring a Google Cloud consultant or working with Google Cloud support.

---

## Access Request Template

### For Users Requesting Access

Copy this email template to request BigQuery access:

```
Subject: BigQuery Access Request - Guttmacher Legislative Tracker

Hi [Administrator Name],

I need access to the Guttmacher Legislative Tracker BigQuery data for [reason: analysis/reporting/research].

My information:
- Name: [Your Full Name]
- Email: [your.email@organization.com]
- Organization: [Your Organization]
- Purpose: [Brief description of why you need access]
- Access level needed: Read-only (to run queries and view data)

I have created a Google Account using my email address following the instructions at:
https://support.google.com/accounts/answer/27441

Please grant me:
- BigQuery Job User role (to run queries)
- BigQuery Data Viewer role (to view data)

For dataset: legislative_tracker_historical

Thank you!
[Your Name]
```

### For Administrators Granting Access

Reply template:

```
Subject: RE: BigQuery Access Request - Granted

Hi [User Name],

Your access to Guttmacher Legislative Tracker BigQuery data has been granted.

Access details:
- Project: guttmacher-legislative-tracker
- Dataset: legislative_tracker_historical
- Roles: BigQuery Job User + BigQuery Data Viewer (read-only)

To access the data:
1. Go to: https://console.cloud.google.com/bigquery
2. Sign in with: [user.email@organization.com]
3. Star the project: guttmacher-legislative-tracker
4. View documentation: [link to your docs site]

Getting started resources:
- BigQuery for Analysts guide: [link]
- Looker Studio dashboards: [link]
- Data dictionary: [link]

If you have any issues accessing the data, please let me know.

[Administrator Name]
```

---

## Managing Access

### Viewing Current Access

**List all users with access:**

```bash
# View project-level IAM
gcloud projects get-iam-policy guttmacher-legislative-tracker \
  --format=json > iam-policy.json

# View dataset-level access
bq show --format=prettyjson guttmacher-legislative-tracker:legislative_tracker_historical
```

**In Google Cloud Console:**

1. Go to [IAM page](https://console.cloud.google.com/iam-admin/iam)
2. Select project: `guttmacher-legislative-tracker`
3. See list of all principals and their roles

---

### Revoking Access

If you need to remove a user's access:

**Option 1: Cloud Console**

1. Go to [IAM page](https://console.cloud.google.com/iam-admin/iam)
2. Find the user in the list
3. Click pencil icon (Edit)
4. Remove BigQuery roles
5. Click "Save"

**Option 2: Command Line**

```bash
# Remove BigQuery Data Viewer role
gcloud projects remove-iam-policy-binding guttmacher-legislative-tracker \
  --member="user:person@organization.com" \
  --role="roles/bigquery.dataViewer"

# Remove BigQuery Job User role
gcloud projects remove-iam-policy-binding guttmacher-legislative-tracker \
  --member="user:person@organization.com" \
  --role="roles/bigquery.jobUser"
```

User will lose access within a few minutes.

---

### Auditing Access

Track who accessed your data:

**Enable Data Access audit logs:**

1. Go to [IAM → Audit Logs](https://console.cloud.google.com/iam-admin/audit)
2. Find "BigQuery" in services list
3. Enable "Data Read" logs
4. Click "Save"

**View access logs:**

1. Go to [Logs Explorer](https://console.cloud.google.com/logs)
2. Query:

```
resource.type="bigquery_resource"
protoPayload.methodName="jobservice.insert"
```

This shows all queries run, by whom, and when.

---

## Troubleshooting

### User Can't See Project

**Error:** "Project not found" or empty Explorer panel

**Solutions:**

1. **Check spelling:** Verify project name is exactly `guttmacher-legislative-tracker`
2. **Star the project:**
   - Click "Add" → "Star a project by name"
   - Enter project name
3. **Verify access was granted:** Check IAM page to confirm user is listed
4. **Wait 5 minutes:** IAM changes can take a few minutes to propagate
5. **Try incognito:** Sign out and sign back in

---

### User Gets "Permission Denied" Error

**Error when running query:** "Access Denied: Table ... User does not have permission to query table"

**Solutions:**

1. **Check roles:** User needs BOTH `BigQuery Job User` AND `BigQuery Data Viewer`
2. **Check dataset:** Verify user has access to correct dataset (`legislative_tracker_historical`)
3. **Check table exists:** Verify table/view name is spelled correctly
4. **Project-level vs dataset-level:** User may have project access but not dataset access (or vice versa)

**To fix - grant dataset-level access:**

```bash
# Grant access to specific dataset
bq add-iam-policy-binding \
  --member="user:person@organization.com" \
  --role="roles/bigquery.dataViewer" \
  guttmacher-legislative-tracker:legislative_tracker_historical
```

---

### User Can't Create Google Account with Existing Email

**Error:** "This email is already in use"

**Cause:** User already has a Google Account with that email (maybe created previously)

**Solutions:**

1. **Try to sign in:** Go to [accounts.google.com](https://accounts.google.com) and try signing in
2. **Recover account:** Use "Forgot password" to recover the existing account
3. **Use different email:** Create Google Account with a different email if available

---

### Authentication Issues

**Error:** "Couldn't sign you in" or "This Google Account doesn't exist"

**Solutions:**

1. **Verify Google Account was created:** Go to [myaccount.google.com](https://myaccount.google.com) and sign in
2. **Check email verification:** Ensure user completed email verification step
3. **Use correct email:** Sign in with exact email used to create Google Account
4. **Clear browser cache:** Try incognito/private browsing mode

---

## Security Best Practices

### Principle of Least Privilege

Grant only the minimum access needed:

| User Type | Recommended Roles |
|-----------|------------------|
| External analyst (read-only) | BigQuery Job User + BigQuery Data Viewer |
| Internal team member | BigQuery Job User + BigQuery Data Editor |
| Administrator | BigQuery Admin |

### Time-Limited Access

For temporary collaborators:

1. Grant access when needed
2. Set calendar reminder to review access
3. Revoke when project ends

**Or use conditional access (advanced):**

```bash
# Grant access with expiration (requires Cloud IAM Conditions)
gcloud projects add-iam-policy-binding guttmacher-legislative-tracker \
  --member="user:temp@partner.org" \
  --role="roles/bigquery.dataViewer" \
  --condition='expression=request.time < timestamp("2025-12-31T00:00:00Z"),title=Expires 2025-12-31'
```

### Audit Regularly

Monthly security checklist:

- [ ] Review list of users with access (remove departed users)
- [ ] Check audit logs for unusual query patterns
- [ ] Verify external users still need access
- [ ] Update documentation when users change

---

## Cost Considerations

### BigQuery Costs

**Free tier (per user, per month):**

- First 1 TB of queries: FREE
- First 10 GB of storage: FREE

**After free tier:**

- Queries: $5 per TB processed
- Storage: $0.02 per GB per month

!!! tip "Typical Usage for Legislative Tracker"
    Most users stay well within free tier:

    - Dataset size: ~500 MB (well under 10 GB free storage)
    - Typical query: Processes 10-50 MB
    - Average user: ~20 queries/month = ~1 GB processed (well under 1 TB free tier)

**To monitor costs:**

1. Go to [Billing](https://console.cloud.google.com/billing)
2. View "BigQuery" charges
3. Set up budget alerts if needed

### Google Account Costs

**Free:** Creating Google Accounts is free. Users pay nothing.

---

## Related Resources

- **[BigQuery for Analysts](../user-guides/bigquery-for-analysts.md)** - Guide for users to query data
- **[Looker Studio Guide](../user-guides/looker-studio-guide.md)** - Visualize data without SQL
- **[Data Dictionary](../reference/data-dictionary.md)** - Understand field definitions
- **[Security & Compliance](security.md)** - Data security policies

---

## Getting Help

**For administrators:**

- Google Cloud IAM documentation: [cloud.google.com/iam/docs](https://cloud.google.com/iam/docs)
- BigQuery access control: [cloud.google.com/bigquery/docs/access-control](https://cloud.google.com/bigquery/docs/access-control)

**For users:**

- Creating Google Account: [support.google.com/accounts/answer/27441](https://support.google.com/accounts/answer/27441)
- BigQuery quickstart: [cloud.google.com/bigquery/docs/quickstarts](https://cloud.google.com/bigquery/docs/quickstarts)

**Contact:**

- Technical issues: Contact the technical team
- Policy questions: Contact the policy team or legal team

---

*Last updated: December 2025*
