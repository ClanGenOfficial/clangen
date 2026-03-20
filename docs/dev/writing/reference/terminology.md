## Warrior-specific Terms

### Seasons
*Do not capitalize, except when beginning a sentence.*
 
Spell and hyphenate as:

- newleaf 
- greenleaf
- leaf-fall
- leaf-bare

### Other Terms

- **Clan** and **Clanmate** is always capitalized, even when Clan is a suffix
- **Gathering** is always capitalized
- **StarClan** is always capitalized
- **Dark Forest** is always capitalized
- **Thunderpath** is always capitalized

- Use **Twolegs**, capitalized with no hyphen. The singular for Twolegs is Twoleg.
- Use **fresh-kill**, always include hyphen
- Use **crowfood**, not ‘rotten fresh-kill’
- If you want the cats to swear, **fox-dung** and **mouse-dung** are always hyphenated

### Warriors Idioms
Try to use phrases from this list when you can instead of using "our" version of it. Just helps a bit with world-building!

- "We'll cross that river when we come to it"
- "Caught two prey with one blow"
- "Pain in the tail"
- "Scaredy-mouse"

## Coding Terms for Writers to Know
- string [str] - Used to refer to a string of text.  For example, patrol events have multiple outcomes and each of those outcomes are individual strings.  Strings are encased between quotations like so `"this is a string."`.
- list - A collection of items held within brackets like so `[item0, item1, item2, item3]`. Note that code starts counting at 0, not at 1.  Also note the comma between each item, this is *required* for the list to work properly.
- dictionary [dict] - Used to hold keys and their values.  Dictionaries are encased by curly braces.  Think of keys as a word in a dictionary, and the value as its definition.  For example:
- 
```python
name_of_dict = {
    "key0": "I am the key's value",
    "key1": ["Values", "can", "be", "lists", "too"],
    "key2": "don't forget that key-value pairs need commas between them!",
    "key3": {
        "you": "can even put dictionaries",
        "inside": "other dictionaries!"
    }
}
```

- integer [int] - A number.  This cannot be a decimal.
- parameter - We use a lot of event formats that have multiple sections to fill out.  Each of these sections is referred to as a 'parameter' in coding language. You can think of it as directions that tell the code what the event is allowed to do.  So in the patrol format, you have the tag parameter, the event text parameter, the success outcomes parameter, the fail outcomes parameter, ect.
- IDE - A code interpreter. These are programs that allow you to view, run, and edit code, they generally provide shortcuts and point out errors to help speed the process. 
- json - a file type. We use these files to hold strings and other important game info.  Nearly all of the strings in the game are held in jsons. Some IDEs, like PyCharm or virtual studio code, are able to help you properly format and spot errors in jsons. I’d recommend using one of those IDEs to help streamline your process.

- Github Terms 
    - github desktop - An application that makes syncing, editing, and committing your code easier. This, along with an IDE, is highly recommended for anyone contributing to the ClanGen game files.
    - repository / repo - In many ways, you can think of a Git repository as a directory that stores all the files, folders, and content needed for ClanGen. What it actually is, is the object database of the project, storing everything from the files themselves, to the versions of those files, commits, deletions, et cetera. Repositories are not limited by user, and can be shared and copied (see: fork).
    - PR - a Pull Request (PR) is how you will merge your code into a repository. Pull requests ask the repo maintainers to review the commits made, and then, if acceptable, merge the changes upstream.
    - merge - Taking the changes from one branch and adding them into another (traditionally master) branch. These commits are usually first requested via pull request before being merged by a project maintainer.
    - pull - A “pull” happens when adding the changes to the master branch. 
    - push - Updates a remote branch with the commits made to the current branch. You are literally “pushing” your changes onto the remote.
    - origin - The conventional name for the primary version of a repository.
    - fork - a fork is a copy of a repository.  This fork is unique to your github account and allows you to make edits without changing the original repository. 
    - branch - A version of the repository that diverges from the main working project. Branches can be a new version of a repository, experimental changes, or personal forks of a repository for users to alter and test changes.

