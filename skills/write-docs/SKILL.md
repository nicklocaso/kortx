---
name: write-docs
description: Write documentation and messages to the user with ASD-STE100 rules. Use it for all text.
---

# Write docs

## Language

- Write repository text in English.
- Write in English the names of the files, folders and branches that you make. This rule also applies outside the repository.
- Exception: keep a name from an external source, for example the name of a downloaded file or an invoice number.
- Exception: use the name that the user gives.
- Write messages to the user in the language of the instance. See `AGENTS.md`. If it is not English, apply the rules only, not the dictionary.

## Rules (ASD-STE100)

### Words

- Use approved words only, with their approved meaning.
- Use one word for one concept. Do not use synonyms.
- Use technical names for parts and actions that are specific to the subject.

### Sentences

- Write procedural sentences with a maximum of 20 words.
- Write descriptive sentences with a maximum of 25 words.
- Write one instruction in each sentence.
- Use the active voice.
- Use the imperative in instructions.
- Use articles ("a", "the") where possible.

### Structure

- Write one topic in each paragraph.
- Write paragraphs with a maximum of 6 sentences.
- Put the most important information first.
- Use numbered lists for steps in a sequence.
- Use bullet lists for items with no sequence.
- Put a warning or caution before the applicable step.

## Format

- Use Markdown.
- Use one `#` heading for each file.
- Use kebab-case for file and folder names.
- Exception: code uses the naming convention of its language. For Python, use snake_case for `.py` files and for package folders.
