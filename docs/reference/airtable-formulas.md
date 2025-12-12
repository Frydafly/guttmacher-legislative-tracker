# Guttmacher Policy Tracker Formulas

This document explains the formulas used in our Airtable base in plain
language. Each formula includes the exact code to use, what it does, how
it works, and how to modify it. You don\'t need to be a technical expert
to understand or use these instructions.

## Introduction Date Formula

### Code Block:

  -----------------------------------------------------------------------
  IF(\
  \
  OR(\
  \
  REGEX_MATCH(History, \'(?s).\*?(\\\\d{2}/\\\\d{2}/\\\\d{4})
  \\\\(\[A-Z\]\\\\) (?i:Introduced\|Introduced and)\'),\
  \
  REGEX_MATCH({StateNet History},
  \'(?s).\*?(\\\\d{2}/\\\\d{2}/\\\\d{4}) - INTRODUCED\')\
  \
  ),\
  \
  IF(\
  \
  AND(\
  \
  REGEX_MATCH(History, \'(?s).\*?(\\\\d{2}/\\\\d{2}/\\\\d{4})
  \\\\(\[A-Z\]\\\\) (?i:Introduced\|Introduced and)\'),\
  \
  REGEX_MATCH({StateNet History},
  \'(?s).\*?(\\\\d{2}/\\\\d{2}/\\\\d{4}) - INTRODUCED\')\
  \
  ),\
  \
  IF(\
  \
  VALUE(SUBSTITUTE(REGEX_EXTRACT(History,
  \'.\*?(\\\\d{2}/\\\\d{2}/\\\\d{4}) \\\\(\[A-Z\]\\\\)
  (?i:Introduced\|Introduced and)\'), \"/\", \"\")) \>\
  \
  VALUE(SUBSTITUTE(REGEX_EXTRACT({StateNet History},
  \'.\*?(\\\\d{2}/\\\\d{2}/\\\\d{4}) - INTRODUCED\'), \"/\", \"\")),\
  \
  REGEX_EXTRACT(History, \'.\*?(\\\\d{2}/\\\\d{2}/\\\\d{4})
  \\\\(\[A-Z\]\\\\) (?i:Introduced\|Introduced and)\'),\
  \
  REGEX_EXTRACT({StateNet History}, \'.\*?(\\\\d{2}/\\\\d{2}/\\\\d{4}) -
  INTRODUCED\')\
  \
  ),\
  \
  IF(\
  \
  REGEX_MATCH(History, \'(?s).\*?(\\\\d{2}/\\\\d{2}/\\\\d{4})
  \\\\(\[A-Z\]\\\\) (?i:Introduced\|Introduced and)\'),\
  \
  REGEX_EXTRACT(History, \'.\*?(\\\\d{2}/\\\\d{2}/\\\\d{4})
  \\\\(\[A-Z\]\\\\) (?i:Introduced\|Introduced and)\'),\
  \
  REGEX_EXTRACT({StateNet History}, \'.\*?(\\\\d{2}/\\\\d{2}/\\\\d{4}) -
  INTRODUCED\')\
  \
  )\
  \
  ),\
  \
  0\
  \
  )
  -----------------------------------------------------------------------

  -----------------------------------------------------------------------

### What it does:

This formula finds the date when a bill was first introduced by
searching through both the bill\'s History AND StateNet History fields.
It compares dates from both fields and selects the most recent one. The
formula is case-insensitive for the word \"introduced\" in the History
field.

### How it works:

The formula searches both fields for specific patterns:

1.  In the History field, it looks for:

    - A date in the format MM/DD/YYYY (like 01/15/2024)

    - Followed by a chamber indicator in parentheses (like (H) or (S))

    - Followed by the word \"Introduced\" (in any case)

2.  In the StateNet History field, it looks for:

    - A date in the format MM/DD/YYYY

    - Followed by \"- INTRODUCED\"

3.  If it finds matches in both fields, it compares the dates and
    returns the more recent one

4.  If it only finds a match in one field, it returns that date

5.  If it doesn\'t find a match in either field, it returns 0

For example:

- In History: \"01/15/2024 (H) Introduced and referred to Committee\"

- In StateNet History: \"01/20/2024 - INTRODUCED.; 01/20/2024 - To
  COMMITTEE.\"

- The formula would return: 01/20/2024 (the most recent date)

### How to modify:

- To change the date format:

  - Find the \\\\d{2}/\\\\d{2}/\\\\d{4} pattern in the formula

  - Adjust it to match your desired date format

  - Make sure to change it in all places in the formula

- To change what text indicates introduction:

  - For History field, find the (?i:Introduced\|Introduced and) part

  - For StateNet History field, find the - INTRODUCED part

  - Add additional terms or modify as needed

- To change what displays when no date is found:

  - Change the final 0 to whatever you want to show instead

  - For example, change it to \"\" for an empty string or \"No date\"
    for text

## Enacted Date Formula

### Code Block:

+-----------------------------------------------------------------------+
| IF(                                                                   |
|                                                                       |
| OR(                                                                   |
|                                                                       |
| REGEX_MATCH(History, \'(?s).\*?(\\\\d{2}/\\\\d{2}/\\\\d{4})           |
| (?:\\\\(\[A-Z\]\\\\) )?(?i:Signed by\|Overridden)\'),                 |
|                                                                       |
| REGEX_MATCH({StateNet History},                                       |
| \'(?s).\*?(\\\\d{2}/\\\\d{2}/\\\\d{4}) -? (?i:SIGNED\|OVERRIDDEN)\')  |
|                                                                       |
| ),                                                                    |
|                                                                       |
| IF(                                                                   |
|                                                                       |
| AND(                                                                  |
|                                                                       |
| REGEX_MATCH(History, \'(?s).\*?(\\\\d{2}/\\\\d{2}/\\\\d{4})           |
| (?:\\\\(\[A-Z\]\\\\) )?(?i:Signed by\|Overridden)\'),                 |
|                                                                       |
| REGEX_MATCH({StateNet History},                                       |
| \'(?s).\*?(\\\\d{2}/\\\\d{2}/\\\\d{4}) -? (?i:SIGNED\|OVERRIDDEN)\')  |
|                                                                       |
| ),                                                                    |
|                                                                       |
| IF(                                                                   |
|                                                                       |
| VALUE(SUBSTITUTE(                                                     |
|                                                                       |
| IF(                                                                   |
|                                                                       |
| REGEX_MATCH(History, \'(?s).\*?(\\\\d{2}/\\\\d{2}/\\\\d{4})           |
| (?:\\\\(\[A-Z\]\\\\) )?(?i:Signed by)\'),                             |
|                                                                       |
| REGEX_EXTRACT(History, \'.\*?(\\\\d{2}/\\\\d{2}/\\\\d{4})             |
| (?:\\\\(\[A-Z\]\\\\) )?(?i:Signed by)\'),                             |
|                                                                       |
| REGEX_EXTRACT(History, \'.\*?(\\\\d{2}/\\\\d{2}/\\\\d{4})             |
| (?:\\\\(\[A-Z\]\\\\) )?(?i:Overridden)\')                             |
|                                                                       |
| ), \"/\", \"\")                                                       |
|                                                                       |
| ) \>                                                                  |
|                                                                       |
| VALUE(SUBSTITUTE(                                                     |
|                                                                       |
| IF(                                                                   |
|                                                                       |
| REGEX_MATCH({StateNet History},                                       |
| \'(?s).\*?(\\\\d{2}/\\\\d{2}/\\\\d{4}) -? (?i:SIGNED)\'),             |
|                                                                       |
| REGEX_EXTRACT({StateNet History}, \'.\*?(\\\\d{2}/\\\\d{2}/\\\\d{4})  |
| -? (?i:SIGNED)\'),                                                    |
|                                                                       |
| REGEX_EXTRACT({StateNet History}, \'.\*?(\\\\d{2}/\\\\d{2}/\\\\d{4})  |
| -? (?i:OVERRIDDEN)\')                                                 |
|                                                                       |
| ), \"/\", \"\")                                                       |
|                                                                       |
| ),                                                                    |
|                                                                       |
| IF(                                                                   |
|                                                                       |
| REGEX_MATCH(History, \'(?s).\*?(\\\\d{2}/\\\\d{2}/\\\\d{4})           |
| (?:\\\\(\[A-Z\]\\\\) )?(?i:Signed by)\'),                             |
|                                                                       |
| REGEX_EXTRACT(History, \'.\*?(\\\\d{2}/\\\\d{2}/\\\\d{4})             |
| (?:\\\\(\[A-Z\]\\\\) )?(?i:Signed by)\'),                             |
|                                                                       |
| REGEX_EXTRACT(History, \'.\*?(\\\\d{2}/\\\\d{2}/\\\\d{4})             |
| (?:\\\\(\[A-Z\]\\\\) )?(?i:Overridden)\')                             |
|                                                                       |
| ),                                                                    |
|                                                                       |
| IF(                                                                   |
|                                                                       |
| REGEX_MATCH({StateNet History},                                       |
| \'(?s).\*?(\\\\d{2}/\\\\d{2}/\\\\d{4}) -? (?i:SIGNED)\'),             |
|                                                                       |
| REGEX_EXTRACT({StateNet History}, \'.\*?(\\\\d{2}/\\\\d{2}/\\\\d{4})  |
| -? (?i:SIGNED)\'),                                                    |
|                                                                       |
| REGEX_EXTRACT({StateNet History}, \'.\*?(\\\\d{2}/\\\\d{2}/\\\\d{4})  |
| -? (?i:OVERRIDDEN)\')                                                 |
|                                                                       |
| )                                                                     |
|                                                                       |
| ),                                                                    |
|                                                                       |
| IF(                                                                   |
|                                                                       |
| REGEX_MATCH(History, \'(?s).\*?(\\\\d{2}/\\\\d{2}/\\\\d{4})           |
| (?:\\\\(\[A-Z\]\\\\) )?(?i:Signed by\|Overridden)\'),                 |
|                                                                       |
| IF(                                                                   |
|                                                                       |
| REGEX_MATCH(History, \'(?s).\*?(\\\\d{2}/\\\\d{2}/\\\\d{4})           |
| (?:\\\\(\[A-Z\]\\\\) )?(?i:Signed by)\'),                             |
|                                                                       |
| REGEX_EXTRACT(History, \'.\*?(\\\\d{2}/\\\\d{2}/\\\\d{4})             |
| (?:\\\\(\[A-Z\]\\\\) )?(?i:Signed by)\'),                             |
|                                                                       |
| REGEX_EXTRACT(History, \'.\*?(\\\\d{2}/\\\\d{2}/\\\\d{4})             |
| (?:\\\\(\[A-Z\]\\\\) )?(?i:Overridden)\')                             |
|                                                                       |
| ),                                                                    |
|                                                                       |
| IF(                                                                   |
|                                                                       |
| REGEX_MATCH({StateNet History},                                       |
| \'(?s).\*?(\\\\d{2}/\\\\d{2}/\\\\d{4}) -? (?i:SIGNED)\'),             |
|                                                                       |
| REGEX_EXTRACT({StateNet History}, \'.\*?(\\\\d{2}/\\\\d{2}/\\\\d{4})  |
| -? (?i:SIGNED)\'),                                                    |
|                                                                       |
| REGEX_EXTRACT({StateNet History}, \'.\*?(\\\\d{2}/\\\\d{2}/\\\\d{4})  |
| -? (?i:OVERRIDDEN)\')                                                 |
|                                                                       |
| )                                                                     |
|                                                                       |
| )                                                                     |
|                                                                       |
| ),                                                                    |
|                                                                       |
| \"\"                                                                  |
|                                                                       |
| )                                                                     |
+=======================================================================+

### What it does:

This formula searches both the bill\'s History and StateNet History
fields to find the date when a bill was enacted, looking for when it was
signed into law or when a veto was overridden. It compares dates from
both fields and returns the most recent one. The formula is
case-insensitive for the enactment terms.

### How it works:

The formula searches through both fields for specific patterns:

1.  In the History field, it looks for:

    - A date in MM/DD/YYYY format (like 03/21/2024)

    - Followed by \"Signed by\" or \"Overridden\" (in any case)

    - Or Followed by letters inside of parenthesis \[like (H) or (S)\]
      and then having signed by or overridden

2.  In the StateNet History field, it looks for:

    - A date in MM/DD/YYYY format

    - Followed by \"- SIGNED\", \"SIGNED\", \"- OVERRIDDEN\", or
      \"OVERRIDDEN\" (in any case)

3.  If it finds matches in both fields, it compares the dates and
    returns the more recent one

4.  If it only finds a match in one field, it returns that date

5.  If it doesn\'t find a match in either field, it returns an empty
    string

For example:

- In History: \"03/21/2024 Signed by Governor\"

- In StateNet History: \"03/22/2024 - SIGNED.\"

- The formula would return: 03/22/2024 (the most recent date)

### How to modify:

- To change what text indicates enactment:

  - For History field, find the (?i:Signed by\|Overridden) part

  - For StateNet History field, find the (?i:SIGNED\|OVERRIDDEN) part

  - Replace or add alternatives as needed

  - Make sure to change it in all relevant places in the formula

- To change the date format:

  - Find the \\\\d{2}/\\\\d{2}/\\\\d{4} pattern

  - Adjust it to match your desired date format

  - Remember to change it throughout the formula

- To change what displays when no date is found:

  - Change the final \"\" to whatever you want to show instead

  - For example, 0 for numeric value, or \"Not enacted\" for text

## Last Action Date Formula

### Code Block:

  -----------------------------------------------------------------------
  IF(\
  \
  AND(\
  \
  NOT({History} = \"\"),\
  \
  NOT({StateNet History} = \"\")\
  \
  ),\
  \
  IF(\
  \
  VALUE(SUBSTITUTE(LEFT({History}, 10), \"/\", \"\")) \>
  VALUE(SUBSTITUTE(LEFT({StateNet History}, 10), \"/\", \"\")),\
  \
  LEFT({History}, 10),\
  \
  LEFT({StateNet History}, 10)\
  \
  ),\
  \
  IF(\
  \
  NOT({History} = \"\"),\
  \
  LEFT({History}, 10),\
  \
  IF(\
  \
  NOT({StateNet History} = \"\"),\
  \
  LEFT({StateNet History}, 10),\
  \
  \"\"\
  \
  )\
  \
  )\
  \
  )
  -----------------------------------------------------------------------

  -----------------------------------------------------------------------

### What it does:

This formula finds the most recent date between the History and StateNet
History fields by comparing the first dates in each (which will be the
latest dates since histories are written with newest events first). It
returns the more recent date between the two fields, or the only date if
just one field has content.

### How it works:

1.  The formula first checks if both History and StateNet History fields
    have content

2.  If both fields have content:

    - It extracts the first 10 characters from each field (the date in
      MM/DD/YYYY format)

    - It converts these dates to numbers by removing the slashes

    - It compares the numeric values and returns the larger (more
      recent) date

3.  If only one field has content, it returns the first 10 characters
    from that field

4.  If neither field has content, it returns an empty string

For example:

- In History: \"03/15/2024 (H) Referred to committee\"

- In StateNet History: \"03/20/2024 - To HOUSE Committee on JUDICIARY.\"

- The formula would return: 03/20/2024 (the most recent date)

### How to modify:

- To change the date format:

  - This formula assumes the date is the first 10 characters in both
    fields

  - If your date format is different, adjust the LEFT({History}, 10) to
    extract the correct number of characters

  - You may need to modify the comparison logic if your date format is
    different

- To change what displays when no date is found:

  - Change the final \"\" to whatever you want to show instead

  - For example, \"No date\" or 0

- To add additional fields to check:

  - Add more nested IF statements to check additional fields

  - Follow the same pattern of checking if the field is not empty and
    comparing dates

## Date Validation Formula

### Code Block:

+-----------------------------------------------------------------------+
| IF(                                                                   |
|                                                                       |
| OR(                                                                   |
|                                                                       |
| AND(NOT(BLANK({Last Action})), IS_AFTER({Last Action}, TODAY())),     |
|                                                                       |
| AND(NOT(BLANK({Introduction Date})), IS_AFTER({Introduction Date},    |
| TODAY())),                                                            |
|                                                                       |
| AND(NOT(BLANK({Passed 1 Chamber Date})), IS_AFTER({Passed 1 Chamber   |
| Date}, TODAY())),                                                     |
|                                                                       |
| AND(NOT(BLANK({Passed Legislature Date})), IS_AFTER({Passed           |
| Legislature Date}, TODAY())),                                         |
|                                                                       |
| AND(NOT(BLANK({Vetoed Date})), IS_AFTER({Vetoed Date}, TODAY())),     |
|                                                                       |
| AND(NOT(BLANK({Enacted Date})), IS_AFTER({Enacted Date}, TODAY())))   |
|                                                                       |
| ,                                                                     |
|                                                                       |
| CONCATENATE(                                                          |
|                                                                       |
| \"🚫 \",                                                              |
|                                                                       |
| IF(AND(NOT(BLANK({Last Action})), IS_AFTER({Last Action}, TODAY())),  |
| \"Last Action \", \"\"),                                              |
|                                                                       |
| IF(AND(NOT(BLANK({Introduction Date})), IS_AFTER({Introduction Date}, |
| TODAY())), \"Introduction Date \", \"\"),                             |
|                                                                       |
| IF(AND(NOT(BLANK({Passed 1 Chamber Date})), IS_AFTER({Passed 1        |
| Chamber Date}, TODAY())), \"Passed 1 Chamber Date \", \"\"),          |
|                                                                       |
| IF(AND(NOT(BLANK({Passed Legislature Date})), IS_AFTER({Passed        |
| Legislature Date}, TODAY())), \"Passed Legislature Date \", \"\"),    |
|                                                                       |
| IF(AND(NOT(BLANK({Vetoed Date})), IS_AFTER({Vetoed Date}, TODAY())),  |
| \"Vetoed Date \", \"\"),                                              |
|                                                                       |
| IF(AND(NOT(BLANK({Enacted Date})), IS_AFTER({Enacted Date},           |
| TODAY())), \"Enacted Date\", \"\")                                    |
|                                                                       |
| ),                                                                    |
|                                                                       |
| \"\"                                                                  |
|                                                                       |
| )                                                                     |
+=======================================================================+

### What it does:

This formula checks all date fields in a record to detect any that have
been set to future dates. When it finds dates set in the future, it
displays a warning with a red stop sign emoji followed by the names of
the problematic fields. If all dates are valid (not in the future), the
field remains empty.

### How it works:

1.  The formula first uses OR() to check if ANY of the date fields
    contain future dates

2.  For each field, it uses AND(NOT(BLANK(field)), IS_AFTER(field,
    TODAY())) to:

    - Confirm the field isn\'t empty

    - Check if the date is after today

3.  If any future dates are found, it builds a warning message:

    - Starts with a stop sign emoji (🚫)

    - Lists only the field names that have future dates

4.  If no future dates are found, it returns an empty string

### How to modify:

- To exclude Effective Date from validation:

  - Simply remove the Effective Date checks from both the OR statement
    and the CONCATENATE statement

- To add additional date fields to check:

  - Add another AND condition to the OR statement for the new field

  - Add another IF statement to the CONCATENATE for the new field

- To change the warning icon:

  - Replace 🚫 with any other emoji or text

- To change the validation rule:

  - Replace IS_AFTER with another comparison if needed
