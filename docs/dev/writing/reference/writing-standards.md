# Writing Standards

- ClanGen is a game that relies on random event generation. This means that whatever you're writing needs to function for all cats it might generate for, under all circumstances it can be generated in.

!!! caution
    No assumptions should be made about the gender of any cat. Nothing in the game is completely gender-locked, including pregnancy under certain settings, so all text should take this into account.

- Remember that the focus of this game is allowing players to build their own story! Most of the time, it’s better not to insert character motivations into the text. We want to leave space for the player to explain and expand upon the events that happen in the game. Of course, there are some trait, skill, rank, or age specific texts that can allow more personality to shine through
- The Dark Forest is not fully implemented yet, and flavor text should not mention it too much at the moment. It exists, but there hasn't been a consensus on the exact implementation yet for things like training in the Dark Forest, or how exactly it operates in ClanGen. For example, if it's a secret to all except those who are chosen to train there, or if it's well-known to all Clan cats.
- If you have something you'd like to do with a patrol or event, but the code doesn't seem to have functionality for it yet, please let a coder know! 

## General Grammar
- We use American spelling!
- Keep it simple!  We do not include direct dialogue within our events and we try to keep the word count of each event low.  
- The classics:
    - you're vs your
        - "Your" is always possessive, while “you’re” = “you are”. If you aren’t sure whether “you’re” should be used in a sentence, imagine the same sentence with “you are” in place of “you’re/your” and see if it still makes sense.
    - than vs then
        - "Than" is used to compare things. For instance "I like cake better than pie." On the other hand, "then" relates to time. 1. "First I brushed my teeth, then I went to work." 2. "If there are no apples left, then please go to the store and get some."
    - to vs too vs two
        - “Too” means “in addition”, “as well”, or "excessively". For example, “Bluestar had some prey too.” Or, "The elder was too old to hunt." Two is, of course, only referring to the number. NGL my method for remembering “to” is just “if too should not be used” LOL but it’s kind of a “directional” word if that makes sense. Shows the relationship between two words, the opposite of “from”.
    - its vs it's
        - “Its” is always possessive. "It’s" is an abbreviation for “it is”. Again, if you’re not sure, try imagining the same sentence with “it is” in place of “its/it’s”.
    - their vs they’re vs there
        - "Their" is possessive. “Their tail”, “their prey”, etc. “There” refers to a place. “They’re” is an abbreviation for “they are”.
    - affect vs effect
        - Less common, but always seems to trip people up. “Affect” is a verb. “The poison has affected them quite strongly.” “Effect” is a noun. “They felt the effects of the poison quite strongly.”
    - cats vs cat’s vs cats’
        - Plurals and possessives! Basically, English grammar conventions are hell. I will try to make it not too confusing with the word cat as an example noun. "Cat's" = single cat, possessive. "The cat's tail." "Cats" = plural, multiple cats, not possessive. "The cats gathered around the High Rock." Cats' = plural possessive. "The cats' nests were lined with fresh moss." 
        - For singular words that end in S, add an apostrophe to make them possessive. For instance, "the crocus' petals". For a possessive plural of a word that ends in S, add "es" to the end, then apostrophe. Random example sentence: "The actresses' rooms were located across the hall."
        - Basically, anytime there's a possessive, you want an apostrophe in there somewhere. If the word ends in S, plural or singular, the apostrophe goes at the end. If the singular form of the word ends in S and it's a plural possessive, add "es" at the end, then apostrophe.  The exception to this is “it’s’ and “its”, where “its” is the possessive form and has no apostrophe.
- All ClanGen game text should follow normal grammar rules for capitalizing the first letter of a sentence, and trying to avoid spelling or grammar typos. We all make typos, don't worry! But this is one of the ways beta testing your new content can help you!
- If you are struggling with remembering or understanding a grammar rule, even one that isn't mentioned in the above list, feel free to message in the writing contributor thread or in other official channels of the Discord server.
- The only exception to the above rule is Thoughts! Thoughts should be structured in such a way that they read as a full sentence if the cat’s name is read at the beginning.  For example: “Thinks about their past mistakes.” is the correct grammar for a Thought, as you could imagine a name at the beginning of the sentence and it would be grammatically correct.  However, the sentence should still be capitalized normally.
Event and flavor text should always use Americanized spelling. 
- Text should always use proper punctuation. Note that we are NOT using double spaces. There should only be a single space after all periods.
- Text should be written in present tense, with the exception of history text and backstories being written in past tense. This is because patrols, events, and thoughts are happening to your cats at this present moment, while history text and backstories are a record of things that happened in the past.
- We are using the Oxford comma. The Oxford comma is used for a list of three or more items. For instance: "He bought eggs, milk, and bread." This sentence uses the Oxford comma. "He bought eggs, milk and bread." This sentence does NOT use the Oxford comma. Please use the Oxford comma.
- Advice for fixing typos: control + F and control + shift + F is your friend, and the computer is going to be able to scan the entire document to find every time you wrote “teh” instead of “the” much faster than you can. If you are trying to fix typos in game files in VSCode, you can also use the search tool (magnifying glass on the left sidebar) to find every instance of a specific typo across all files in the currently-open folder and rapidly find and replace. Very useful for patrols, which often have many different iterations of the same text across different files.
- If a code abbreviation (such as o_c_n) needs an ‘a’ or ‘an’ to precede it, always use “a”.  We have code in place to dynamically adjust ‘a’ and ‘an’ depending on the word that replaces the abbreviation.
- HTML tags for bolding and italicizing are usable. These tags are:
    - `<i>` and `</i>` for italicizing
    - `<b>` and `</b>` for bolding
- Keeping a change log: as a writer, people are going to be super excited to experience what you write! Make sure to keep a rough record of what that might be. For example, a writer may have no idea how many fox patrols they are adding total. However, they do know how many species they have added and in what biomes. So, when they make the PR to merge them into the game, they can mention their existence in the changelog for that PR.
    - An easy way to keep track of your additions is with your commit titles and descriptions.  Making commits whenever you reach a ‘milestone’ of sorts and then titling it appropriately will leave you with a nice list of commits to review for your later change log.  When I bugfix, for example, I tend to make a commit every time I fix a bug and then title that commit with a short description of the bug I fixed.

## Upsetting vs graphic content
!!! caution
    ClanGen contains content that is designed to cause distress. There is no way around it, and it is intentional, and it is **not malicious**. Players are supposed to care about the death of a cat, or a cat being injured, or the Clan not having enough food. Writers for ClanGen spend our time trying to provoke emotions in players, both good, positive, happy emotions, and sad ones, or feelings of injustice, or loss. Video games as a medium, especially a story generator like ClanGen, are designed to need active investment from a player on many levels, including emotional.

- There is an important difference between upsetting content and graphic content. 
- ClanGen follows the warriors canonical levels of graphic content and gore. **This is not a non-graphic book series.** For example, in warriors canon Scourge gets an extensive scene where he takes all of Tigerstar(the first)'s lives at once by ripping out his throat. This would be the absolute maximum graphic content allowed in ClanGen.
- However, everyone has far different levels of comfort with regards to graphical content, particularly written graphical content rather than visual. We have needed to edit content to be less graphic before. We will doubtless do so again in the future. When we receive feedback that game text is particularly upsetting, it's important to take that feedback and carefully consider it. This does not always mean removing that content - but we must carefully consider it.
- Graphical content is not limited to violent content. Illness, injury, pregnancy - no one wants to read a play by play of a cat giving birth in extreme graphical detail. 
- This is one of the reasons the development version of the game exists. By playing the development version, people have accepted they may be exposed to features that aren't ready for the stable release of the game yet, including upsetting content that is being playtested.
- People have drastically different levels of comfort for graphical content for kittens (and sometimes apprentices) than for adult characters. This does not mean that nothing upsetting should ever be allowed to happen to kittens, but it's worth considering. 
- For distressing content, aim to use text that is emotive and provokes an emotional response, without using descriptive imagery that is likely to provoke disgust. The diarrhea illness progression and reaction texts are a good example of this. It's an illness that's actually reasonably dangerous, but the text tries to communicate that without focusing on the shitting uncontrollably part. 


## Being Mindful of Disabilities
_by grif_

When writing events related to permanent conditions, we need to be very mindful to avoid ableist rhetoric and inspiration sensationalism.  Some key points to avoid are as follows:

- The idea that a cat is closer to a kitten than an adult
>EG: "crawling" for paralysed cats - this implies they are weaker and also implies they are kit-like. This then takes away the paralysed cat's perceived ability to decide for themself, even though it's accidental. 
>
>INSTEAD: use "clambering", "climbing", "stalking" - these allow a paralysed cat to give themselves agency. 
>
>EXCEPTIONS: "Dragged" can be used in an emotional usage, such as "Poppyheart... drags herself to her front paws, complaining about dawn patrol". 

- The idea that a cat "isn't" effected by their disability
>EG: "Wolfclaw... is proud that they can still work like the rest of the clan." This makes it seem like the cat is comparing themselves to the abled cats, and sets up standards where a disabled cat cannot show their disability. This eventually means you're implying it's somehow "lesser" to be disabled. It might make sense for an insecure cat, but be careful!
>
>INSTEAD: Allow the disability to effect them, and focus on their personal achievements rather than comparing them to other cats. 
>
>EXCEPTIONS: "Raspy lungs", "joint pain", "allergies", "persistent headaches", "constantly dizzy", "recurring shock" - you can reword these into being happy their disability isn't as harsh this moon. These disabilities all come in "waves", where you can have a few days where you aren't as affected, and a few days where you're effected lots. 

- The idea that a disability is only negative
>EG: Any thoughts that give the idea that they'd prefer to be dead, excessive sadness about being disabled, etc.
>
>INSTEAD: Balance the thoughts out! Give them good thoughts alongside the bad! 

- The idea that disabled cats can't make their own choices
>EG: Excessive thoughts that imply a cat asking for another's opinion. 
>
>INSTEAD: Balance out the thoughts. Treat it like any other cat!
>
>EXCEPTIONS: Personality basis - insecure/gloomy/charismatic cats are more likely to ask for other opinions on personal things. 

- The idea that disability is inherently worse than being abled
>EG: Thoughts that imply shame or inherent upset about being disabled, comparison to abled cats, etc.
>
>INSTEAD: Use benign embarrassment! Maybe a cat with lasting grief fell asleep during a ceremony, or a cat with partial hearing loss misheard a request and brought moss instead of a mole.

When in doubt, please ask for feedback! We have multiple disabled contributors on the team and they've lended us their valuable perspectives time and time again.

