
# Common Errors
## Extra (trailing) commas

Trailing commas occur whenever a comma is added after a piece of code that has nothing following, in which JSONS are unable to read the rest of the code and throw errors out. Some examples of trailing commas include:

![Screenshot 2024-04-17 083130](https://github.com/CL0WNTH0UGHTS/Summoners-Clownthoughts-Death-Events/assets/124001594/b41ee9f7-165b-4a60-92bf-4cf4215f4b97)
![Screenshot 2024-04-17 083009](https://github.com/CL0WNTH0UGHTS/Summoners-Clownthoughts-Death-Events/assets/124001594/2daaf497-2239-40a0-b3f6-1ca1014a7dd1)

To fix trailing commas, a good start is to copy what you have added/edited and paste it into `https://jsonlint.com/`. The tool checks if there are any fancy characters (non-ASCII), trailing commas, or missing commas, then directs you and what to remove/add.

![Screenshot 2024-04-17 181501](https://github.com/CL0WNTH0UGHTS/Summoners-Clownthoughts-Death-Events/assets/124001594/85bd9d05-7498-4d32-bdc7-cbe277fe131e)
![Screenshot 2024-04-17 181525](https://github.com/CL0WNTH0UGHTS/Summoners-Clownthoughts-Death-Events/assets/124001594/70fcfdc1-f956-4b40-9fc0-716b9e04e2b2)

## Missing commas

Missing commas occur whenever a comma separating two "keys-values" is deleted or left off, leaving the JSON unable to fully read the code. Some examples include:

![Screenshot 2024-04-17 185427](https://github.com/CL0WNTH0UGHTS/Summoners-Clownthoughts-Death-Events/assets/124001594/a38f0652-b9c7-4a28-a2d2-ae8a80ef7eaf)

To fix missing commas, a good start is to copy what you have added/edited and paste it into `https://jsonlint.com/`. As previously mentioned, the tool checks if there is any issues within the JSON, and notifies if there is any.

![Screenshot 2024-04-17 185356](https://github.com/CL0WNTH0UGHTS/Summoners-Clownthoughts-Death-Events/assets/124001594/4a4f43f0-9733-4f30-b124-63a7f71bd832)


## Non-ASCII characters

Non-ASCII characters (characters not in the American Standard Code for Information Interchange) are often due to fancy quotation marks (“”) or misplaced characters. Some examples include:

![Screenshot 2024-04-17 190152](https://github.com/CL0WNTH0UGHTS/Summoners-Clownthoughts-Death-Events/assets/124001594/1f9cadb6-df9b-437f-93bc-4d2a53bb729d)

To fix or identify non-ASCII characters, a good place to start is to copy what you have added/edited and paste it into `https://jsonlint.com/`. As previously mentioned, the tool checks if there are any issues within the JSON, and notifies if there is any.

![Screenshot 2024-04-17 190457](https://github.com/CL0WNTH0UGHTS/Summoners-Clownthoughts-Death-Events/assets/124001594/a98ee226-e167-4710-9c54-9e1127a04064)

## Error2
With the creation of a pronoun system, all new events going into the official developmental version of ClanGen should be pronoun and verb tagged beforehand, just to make the transition smoother. If, while editing or adding new thoughts to any of the jsons, you boot up the game and notice your thought shows "error2" in place of a pronoun or verb, then there was a misspelling or mis-formatting of the code.



## Pronoun tags
Pronoun tags are the code replacements for singular they/them within the text, as it sets up a framework for custom pronouns to be used instead of ClanGen relying on being gender neutral within the text. The pronouns are represented by {PRONOUN/cat/pronoun}, with cat representing any acronym that can be replaced by a cats name (m_c, r_c, p_l, s_c, etc) and pronoun representing the type of pronouns used (subjective, objective, possessive, etc). If the code was to get messed up in any way (IE misspelling subjective, or doing r_l), then it creates an error2 message within the thought.

![Screenshot 2024-04-17 111107](https://github.com/CL0WNTH0UGHTS/Summoners-Clownthoughts-Death-Events/assets/124001594/16a82903-a1a6-48eb-ac5c-3adae8d665f8)

The best ways to fix this is to first, double check that all the pronouns are properly tagged and rely on copy and pasting the actual filled out versions of the code, or to copy and paste your code into [ClanGen Pronoun Tag Tester (cgen-tools.github.io)](https://cgen-tools.github.io/pronoun-tester/), which will show if the thought has an error in the tagging and makes sense given different pronouns


## Verb tags
Verb tags, much similar to pronoun tags, serve to procedurally change verbs to match a cat's chosen pronoun. In ClanGen, they/them is used both singular and plural, thus the text uses verbs that make sense grammatically (are instead of is, were instead of was, or have instead of has), however custom pronouns will need their specific verbs. Consequently, verbs that need to be changed when pronouns are changed, are replaced with {VERB/cat/plural/singular}; cat representing any acronym that can be replaced by a cats name (m_c, r_c, p_l, etc) while plural/singular represent the versions of the verb.

![Screenshot 2024-04-17 211211](https://github.com/CL0WNTH0UGHTS/Summoners-Clownthoughts-Death-Events/assets/124001594/7a2f04b8-1eac-4beb-a126-dce836a2e95f)

The best ways to fix this is to first, double check that all the pronouns are properly tagged and rely on copy and pasting the actual filled out versions of the code ( {VERB/cat/plural/singular} ), or to copy and paste your code into [ClanGen Pronoun Tag Tester (cgen-tools.github.io)](https://cgen-tools.github.io/pronoun-tester/), which will show if the thought has an error in the tagging and makes sense given different pronouns
