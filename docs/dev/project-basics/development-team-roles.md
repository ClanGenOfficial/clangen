# Development team roles

## Team Roles

<div class="grid cards" markdown>

- __Beta Tester__

    ---

    Players who help us test the dev version of the game and have been given access to beta tester discord channels after application acceptance. 

    [Expections](#beta-tester-expectations){ .md-button .md-button--primary}

- __Apprentice Developer__

    ---

    Developers who have been added to the team via application acceptance, but have not yet contributed to the dev or base game.

    [Expections](#apprentice-developer-expectations){ .md-button .md-button--primary}

- __Developer__

    ---

    Contributors who have had a PR accepted and intend to continue contributing to the project. 

    [Expections](#developer-expectations){ .md-button .md-button--primary}

- __Senior Developer__

    ---

    Developers who have contributed signifcantly to the project and have the responsibility of reviewing PRs. These developers are expected to help steer the team and preserve game identity.

    [Expections](#senior-developer-expectations){ .md-button .md-button--primary}

</div>


## Beta Tester Expectations

### Activity expectations 

- Beta testers are expected to have been active within the last three months. "Activity" is defined as any message within the betatesting channels (⁠dev-version-discussion and its threads + ⁠dev-version-tech-help), but there is some leeway to the time depending on the activity of development and what is there to currently test (it's not your fault if we give you nothing to test).

### Bug Reports are made through Github:
All bugs must be reported to the [ClanGenOfficial Github](https://github.com/ClanGenOfficial/clangen/issues) issues page.

1. Search the existing issues for your bug. If a post already exists for that bug, don't make a new one. Please comment on the currently-existing issue to let us know that you are experiencing the issue as well, with as many screenshots as you can. 
    1. This is especially relevant for typos and spelling errors, which should all be collected under the pinned typo issue.

2.  If a post for your bug doesn't already exist, make one! You'll see a "New Issue" button on Issues page. Enter a title that is clear, specific, and easily searchable. Add any additional information (such as images, instructions to replicate) in the body of the issue. 

3.  Soon, a senior dev will review your issue, and give it appropriate tags.

### Playtesting

Betas are often invited to playtest private, in development features before they go public. Remember to confine your discussion of these features to the private testing threads and never share links to these private branches. 

!!! caution
    If you repeatedly break confidentiality, you are liable to be kicked from the beta testing program without warning.

## Apprentice Developer Expectations
Be sure to check out the [Developer Expectations](#developer-expectations) for further helpful information.

### Activity expectations

- We expect apprentice developers to contribute to the ClanGen development version within 3 months of getting the apprentice developer role. If you take longer and lose the role due to inactivity, you're always welcome to reapply to be a developer!

### Collaboration
- Clangen is all about collaboration. We need to be flexible with each other when developing the game, and open to having our work edited, improved, and iterated on.
- Therefore, please be kind and constructive toward your fellow developers.
- We want to bring apprentice developer's attention to the `good-first-issue` label in our [github issues](https://github.com/ClanGenOfficial/clangen/issues)!  This label is given to issues that senior devs feel will be relatively simple to handle or will make a good introduction to the codebase.  We encourage you to check out issues with this label and consider working on them.  Feel free to ask for help from other contributors, these are meant to be learning experiences!
- Make use of the private developer channels in the server to get to know fellow devs and find good places to start contributing.

### Getting the full developer role
- You'll get your full developer role when you have gotten content into the developmental version of ClanGen, or into a private branch for a new ClanGen feature/content update that is overseen by a senior developer.
- While an apprentice developer, you can't make private testing threads. Ask a more senior dev to make one for testing out your game changes if you feel it's needed.


## Developer Expectations

### Activity expectations

- You must be at least somewhat active in order to keep this role. 
- Don't fret, though, our current cutoff is two months with no activity. 
- This may be subject to change, but you'll be warned ahead of time. 
- If you know you won't be active for a bit, you should request the DEV IN HIATUS role. 
- You will not lose your developer role if you have the hiatus role on unless you have been completely inactive for over 9 months (with no communication).
- Activity is defined as both making PRs to contribute to game milestones, but also contributing to discussions, pitching ideas, offering critique, and planning in the development channels and forum. 

### PR Ettiquette

* PRs that include significant code-base changes should also include appropriate documentation changes. If a PR is made without accompanying documentation, a senior dev may request the addition of documentation.
* PRs should be as small in scope as possible and should only contain singular features/changes. For example, you should not create a PR that includes both art additions and bugfixes. Instead, that PR should be split into two: one for the art additions and a second for the bugfixes. Remember that the larger in scope a PR is, the longer it will take for a senior dev to review and merge it.
* When creating a PR, please pay attention to the built-in template.
* You *must* provide proof of testing for your PR and ensure that all built-in tests pass. If your PR fails a test, please address the issue promptly.
* You are welcome to request reviews from specific senior developers.
    - Fable, Selkirks, and Tiri all oversee writing content additions.
    - Anju oversees cat sprite, clan symbol, and patrol art additions.
    - Scribble oversees camp background and clan symbol additions.
    - Sable, Key, Archanym, Coffee, J-gynn, Lixxis, Scribble, and Anju oversee code-base additions.
* Keep an eye out for merge conflicts on your PR and address them promptly.

### Private Testing Creation
If you have a new feature that you feel needs extensive testing before merging with the main repo then you are welcome to recruit beta testers to assist you.

1. Create a **thread** within the #dev-version-discussion channel. 
2. Ensure that this thread has a clear title and detailed description. Descriptions should include a link to your branch and detailed expectations of what beta testers should be testing for and how they should relay their feedback.
3. Ping the beta tester role. If beta testers need tech support in any fashion, encourage them to seek it in the #dev-version-tech-help channel.

## Senior Developer expectations

Senior developers are those with write access to the ClanGen GitHub. Nothing can be merged to ClanGen without the approval of a senior developer.

If a Pull Request is meant to fix an issue, please ensure the following: Check (or have the developer check) whether the bug affects the latest release branch, too. If it does:

1. Tell the developer to change the target branch of their Pull Request to the latest release branch. For example, release-0.10
2. Ensure that the Pull Request only contains the bugfixes. New features, pelts, sprites, [...] don't belong in a bugfix; there's some exceptions like the Halloween toggle, but usually we want to make sure that there's no gameplay difference between... let's say v0.10.0 and v0.10.5
3. You may review and approve as per usual; but we'd ask you to refrain from making merges to the release branches though


