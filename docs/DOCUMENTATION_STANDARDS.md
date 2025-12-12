# Documentation Standards

## Purpose

This guide explains how we write technical documentation for the Guttmacher Legislative Tracker. Following these standards ensures documentation remains accurate as policies and priorities evolve.

## Core Principle: Technical vs. Policy Separation

### What Belongs in Technical Documentation

Technical documentation describes **HOW the system works**, not **WHEN or WHY to use it**.

✅ **Include in technical docs**:
- HOW to use features and fields
- WHAT the system does when you perform actions
- WHAT fields and options exist
- HOW data flows through the system
- HOW to troubleshoot technical errors

❌ **Exclude from technical docs**:
- WHEN to use specific features (policy decisions)
- WHAT content to write in fields (editorial decisions)
- WHY certain bills need specific treatment (policy priorities)
- WHICH bills to prioritize (team workflow decisions)

### Example Transformations

#### Bad (Prescriptive - Policy Decision)
> "Website blurbs are required for bills with status 'Enacted' or 'Vetoed'."

**Problem**: Makes a policy decision about what's "required"

#### Good (Descriptive - System Behavior)
> "The Website Export script includes bills in the export when status is 'Enacted' or 'Vetoed' AND the Website Blurb field is filled. Your team determines which bills receive website blurbs."

**Why it's better**: Describes what the system does, lets team decide how to use it

---

## Writing Field Descriptions

Use this consistent format for all field descriptions:

```
**[Field Name]**
- Type: [Single select / Long text / Formula / etc.]
- Auto-populated: [Yes/No]
- Used by: [Which scripts/automations use this]
- Purpose: [What it's for in one sentence]

[1-2 sentences describing technical behavior]

[Optional: Technical constraints - character limits, format requirements, etc.]
```

**Example**:

```
**Website Blurb**
- Type: Long text
- Auto-populated: No
- Used by: Website Export script
- Purpose: Public-facing bill description displayed on website

The Website Export script copies content from this field to the Website Exports table. Only bills with filled Website Blurb AND status "Enacted" or "Vetoed" are included in the export.

Technical constraints: Plain text only (no formatting preserved), no character limit.
```

---

## Writing Examples

### Avoid Temporal Content

Examples that include specific dates, political figures, or real bills go out of date quickly.

❌ **Don't use temporal examples**:
> "Good example: In April, Gov. Kay Ivey (R) signed legislation (S 102) that provides presumptive Medicaid eligibility..."

**Problems**:
- Governor names and parties change
- Specific months/bills become outdated
- Implies this is the "correct" content to write

✅ **Use structural templates instead**:
> **Template**: "[Month], [Governor name (Party)] [action] legislation ([Bill ID]) that [policy description]. [Effective date if known]."
>
> **Sample**: "In April, Governor Smith (R) signed legislation (S 102) that expands Medicaid eligibility for prenatal care. The law takes effect in October."

### When Examples Are Helpful

Examples ARE helpful for:
- Showing data structure (field hierarchies, relationships)
- Demonstrating technical formatting (how dates appear, how formulas work)
- Illustrating system behavior (what happens when you click X)

Use generic, made-up data for examples.

---

## Avoiding Prescriptive Language

### Prescriptive Language (Avoid)

Words that make policy decisions or judge correctness:

- "You must..."
- "You should..."
- "Required for..."
- "Best practice is..."
- "Always do..."
- "Never do..." (unless it's a technical constraint)
- "Good example" / "Bad example" (when referring to content)

### Descriptive Language (Use)

Words that describe system behavior or common workflows:

- "The system does..."
- "Most users follow this workflow..."
- "This field is used for..."
- "When you [action], the system [response]"
- "Your team determines..."
- "Technical requirement:" (when it truly is technical)

### Transformation Examples

| Prescriptive | Descriptive |
|--------------|-------------|
| "You must fill in Website Blurb for enacted bills" | "Bills with filled Website Blurb are included in exports" |
| "Best practice: Be specific with categorization" | "Most users select the most specific policy category available" |
| "Always consult legal team for complex bills" | "For complex legal questions, policy team often coordinates with legal team" |
| "Never edit formula fields directly" | "Formula fields auto-update; direct edits will be overwritten" ← This is OK - technical constraint |

---

## Section Structure

When documenting a feature or workflow, use this structure:

### 1. What It Is (Technical Description)
Brief technical description of the feature/field/process

### 2. How It Works (System Behavior)
What the system does technically - data flows, automations, calculations

### 3. How to Use It (Procedures)
Step-by-step instructions for using the feature

### 4. Technical Notes (Constraints & Details)
- Field types, character limits, formatting rules
- What happens behind the scenes
- Relationships to other features

### 5. Troubleshooting (If Applicable)
Common technical errors and how to fix them

---

## Who Decides Policy vs. Who Writes Docs

**Technical documentation** (this repository):
- Maintained by: Technical team
- Describes: How the system works
- Audience: Anyone using or maintaining the system

**Policy documentation** (separate - internal Google Docs):
- Maintained by: Policy team, legal team, editorial team
- Describes: When to use features, what content to create, why priorities exist
- Audience: Policy team members

**Where they connect**: Technical documentation can reference that "your team's workflow determines..." or "your editorial process decides..." without prescribing what that process is.

---

## Quick Checklist for Documentation Reviews

Before committing documentation changes, check:

- [ ] Does this describe HOW the system works, not WHEN to use it?
- [ ] Are examples generic (no governor names, no specific dates)?
- [ ] Does language describe system behavior, not prescribe user behavior?
- [ ] Are field descriptions in consistent format?
- [ ] Would this documentation still be accurate if our policy priorities changed?
- [ ] Can a non-technical team member understand the procedures?

---

## Questions?

For questions about these standards or documentation updates:
- Technical questions: Contact technical team
- Policy questions: Contact policy team

*Last updated: December 2025*
