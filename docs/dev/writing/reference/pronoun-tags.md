
# Pronoun Tags

There are three kinds of pronoun tag: `PRONOUN`, `VERB` and `ADJ` tags.

### A note on plural pronouns
Though less relevant in English, the ability to specify plural pronouns is provided. The format is slightly different:
```
{PRONOUN/PLURAL/m_c+r_c/subject/CAP}
{VERB/PLURAL/m_c+r_c/conju_0/conju_1/[...]/conju_n}
{ADJ/PLURAL/m_c+r_c/gender_0/gender_1/[...]/gender_n}
```
The addition of `PLURAL` immediately following the tag identifier signals that it's a plural pronoun and to use the relevant system. Each cat that is to be referred to by the plural must be referenced in this block, separated by a `+`. Otherwise, the system is the same as below for singular pronouns.

## PRONOUN
A `PRONOUN` tag has three main sections: the `PRONOUN` identifier, the relevant cat, and which pronoun is being requested. There is an optional modifier at the end - `CAP` - that is used to signal that the requested pronoun should be capitalized.

Example:
```
{PRONOUN/m_c/subject}
{PRONOUN/m_c/subject/CAP}
```
Permitted pronouns and their English equivalents:

| Pronoun   | English equivalent       |
|-----------|--------------------------|
| `subject` | he/she/they              |
| `object`  | him/her/them             |
| `poss`    | his/her/their            |
| `inposs`  | his/hers/theirs          |
| `self`    | himself/herself/themself |

## VERB
A `VERB` tag has a technically-infinite number of sections depending on the language, but in English it has four sections: the `VERB` identifier, the relevant cat, and the options for each conjugation in the language (in the case of English, plural and singular conjugations).

Example:
```
{VERB/m_c/were/was}
```

!!! caution
    Pay close attention to the order of verbs. In English, **plural conjugation is first**.

## ADJ
Not especially relevant for English, the `ADJ` tag exists to allow items in a sentence to be referred to with the correct grammatical gender. An English example of gendered words could be actor/actress.

Example:
```
{ADJ/m_c/parent/father/mother}
```
