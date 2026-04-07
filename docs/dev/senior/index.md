# Senior Developers
Senior Developers are team members who have contributed signifcantly to the project and have the responsibility of reviewing PRs. These developers are expected to help steer the team and preserve game identity.

## Release Checklist
This is a list of requirements and instructions for performing a release.

!!! note 
    The checkboxes are not persistent over page reloads. They're just there for reference, so you can check them off as you do a release.

### Prerequisites
#### Major release
- [ ] Promo art is ready
- [ ] Release blurb (for social media) is ready
- [ ] Changelog is ready
#### Patch
- [ ] Changelog is ready

### How to Cut a Release
#### Prepare release branch
- [ ] For a new **major release**, create a new release branch (e.g. `release/0.13.x`. The `x` is there to represent all the patch versions under the release)
    - [ ] Make sure that you counted up properly from the previous version so we don't accidentally skip any numbers
#### changelog.txt
- [ ] On the release branch, open `changelog.txt`
    - [ ] If it's a **major release**, clear the entire log and start new ([example](https://github.com/ClanGenOfficial/clangen/blob/3109d308c023744f4d7d002ab8ca91fe27029bdd/changelog.txt))
    - [ ] If it's a **patch**, add the current version number as heading and add what has been fixed ([example](https://github.com/ClanGenOfficial/clangen/blob/5131bbf06538c522dcec66db34bc69dba4f7c9da/changelog.txt))
- [ ] Make sure that `changelog.txt` DOES NOT contain things like directional quotes (`“` or `”`)
- [ ] Push your `changelog.txt` changes
#### Publishing the release
- [ ] <a href="https://github.com/ClanGenOfficial/clangen/releases" target="_blank">Go to the releases page on GitHub</a>
- [ ] Click `Draft a new release`
- [ ] Change the `Target` to the release branch (e.g. `release/0.13.x`)
- [ ] Under `Select Tag`, press `Create New Tag`
- [ ] Enter a new tag name starting with `v` for the new version (e.g. `v0.13.0`)
- [ ] Fill out the release title. It should be the same as the tag name (e.g. `v0.13.0`)
- [ ] Add the changelog for the release under `Release notes`
    - [ ] If it's a **major release**, add the whole changelog
    - [ ] If it's a **patch**, you only need to add the fixes for that patch
- [ ] Make sure `Set as pre-release` is *not* checked (should be unchecked by default)
- [ ] Make sure `Set as the latest release` *is* checked (should be checked by default)
- [ ] Press `Publish Release`

### Post-release Checklist

- [ ] Contact moderators to announce update on Discord and social media
- [ ] Check to make sure that the release has been successfully uploaded to itch.io, clangen.io, and GitHub