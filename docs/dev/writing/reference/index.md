# Reference 
This page contains formatting information that is generally utilized across all event formats and should be treated as a main reference.

## Pronoun Tags

There are three kinds of pronoun tag: `PRONOUN`, `VERB` and `ADJ` tags.

#### A note on plural pronouns
Though less relevant in English, the ability to specify plural pronouns is provided. The format is slightly different:
```
{PRONOUN/PLURAL/m_c+r_c/subject/CAP}
{VERB/PLURAL/m_c+r_c/conju_0/conju_1/[...]/conju_n}
{ADJ/PLURAL/m_c+r_c/gender_0/gender_1/[...]/gender_n}
```
The addition of `PLURAL` immediately following the tag identifier signals that it's a plural pronoun and to use the relevant system. Each cat that is to be referred to by the plural must be referenced in this block, separated by a `+`. Otherwise, the system is the same as below for singular pronouns.

### PRONOUN
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

### VERB
A `VERB` tag has a technically-infinite number of sections depending on the language, but in English it has four sections: the `VERB` identifier, the relevant cat, and the options for each conjugation in the language (in the case of English, plural and singular conjugations).

Example:
```
{VERB/m_c/were/was}
```

!!! caution
    Pay close attention to the order of verbs. In English, **plural conjugation is first**.

### ADJ
Not especially relevant for English, the `ADJ` tag exists to allow items in a sentence to be referred to with the correct grammatical gender. An English example of gendered words could be actor/actress.

Example:
```
{ADJ/m_c/parent/father/mother}
```


## Writing Histories
Cats receive history text to go with each scar-able injury as well as possibly-fatal injury and direct deaths.  These histories show up in their profile.  Many event formats require you to include the history text if a cat is being injured or killed.  These typically refer to three different history types: `scar`, `reg_death`, `lead_death`.  Following are the guidelines for writing each:

| history type | guidelines                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
|--------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| scar         | This history is given to a cat who gains a scar from an injury gotten during the event.  ONLY INCLUDE if the injury being given is able to scar (i.e a bruise will not scar, but a claw-wound will scar).  This should be a single, full sentence specifying how the cat was scarred.                                                                                                                                                                                                                                                                                                                                                                               |
| reg_death    | This history is given to a non-leader cat who is either killed by the event or dies from an injury gotten during the event.  This should be a single, full sentence specifying how the cat died.  Try not to get too wordy with these.                                                                                                                                                                                                                                                                                                                                                                                                                              |
| lead_death   | This history is given to a leader cat who is either killed by the event or dies from and injury gotten during the event.  This should be a sentence fragment.  Leaders are able to die multiple times, so on their profiles their deaths are listed in one single sentence.  This sentence is formatted as such: "[leader name] lost a life when they [lead_death sentence fragment]" with each following death being added on to create a list with a comma between each item (and the last list item being added with an "and").  Your lead_death text must be able to work within this grammar format and should not include punctuation at the end of the text. |

**Example of acceptable histories**
```json
{
    "scar": "m_c gained a scar from a fox.",
    "reg_death": "m_c died from a fox bite.",
    "lead_death": "died from a fox bite"
}
```
