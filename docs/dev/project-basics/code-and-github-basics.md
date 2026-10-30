On this page, you can find:

1. [Terms to Know](#terms-to-know)
2. [How to Start with GitHub and IDEs](#getting-started-with-github-and-ides)
3. [How to Create a Sister Fork (Advanced)](#sister-forks)


## Terms to Know

#### Git
Git is a distributed version control system. It allows many versions of ClanGen to exist across different forks and branches, which is how developers can make their own changes and then merge those changes into the ClanGen repository. (If you don’t understand any of that, it’s okay; you don’t need to know how Git works. You just need to download it!)

#### GitHub
GitHub is a website and desktop application that ClanGen’s development uses as its central platform for all code changes. This is where you can download the development version of the game, clone it on your computer, commit changes, and open pull requests. Create a GitHub account and download the desktop app if you don’t already have them!

#### Repositories
Repositories are code projects. ClanGen is a repository! Standalone mods like LifeGen are repositories too.

#### Forks
Forks are clones of existing repositories. To start contributing to ClanGen, you will fork the ClanGen repository so that you have your own version of ClanGen on your computer that you can freely edit through GitHub and your IDE. Every developer has their own fork. It’s possible to work on somebody else’s fork, but that is rare and more advanced.

#### Branches
Branches are based off forks; on a branch, you can make changes to the game that you will later merge into the game with a Pull Request. As a developer, you will make lots and lots of branches! You could make one branch to fix a bug, or a branch to add a new feature entirely!

Think of repositories like trees. Imagine that the ClanGen repository is one of these trees. The ClanGen tree has several branches representing its changes and history. A fork is like a copy of the ClanGen tree. This fork has its own branches, which may end up growing differently from the branches on the original tree.

#### Pull Requests
Pull Requests are how you move changes from your own personal branch to the main repository itself! As you edit your branch, the option to “commit changes” will appear in your GitHub Desktop. Once you have finished making and committing changes, you can open a Pull Request. You can view currently open Pull Requests on the ClanGen GitHub to get an idea of what they are. Check out the Pull Request Guide for an in-depth rundown of Pull Requests in general and ClanGen’s etiquette in particular.

## Getting Started with GitHub and IDEs

1. **Make a GitHub account** (https://github.com/)
2. **Set up GitHub Desktop** (https://desktop.github.com/download/)
3. **Install Git**

    > Install git on windows using https://git-scm.com/download/win

    > You can check if you have git installed by entering the command git --version in terminal

4. **Log into GitHub in GitHub Desktop**

    > Git may be set to sign your commits with your email. If you would like your email to remain anonymous, see see [Setting your commit email address on GitHub](https://docs.github.com/en/account-and-profile/setting-up-and-managing-your-personal-account-on-github/managing-email-preferences/setting-your-commit-email-address) and [Configuring your global author information](https://docs.github.com/en/desktop/configuring-and-customizing-github-desktop/configuring-git-for-github-desktop)

6. **Download an IDE** (Integrated Development Environment) to edit the code in. An IDE is to code what Microsoft Word is to writing. Most of the development team uses either [Visual Studio Code](https://code.visualstudio.com/download?_exp_download=d53503e735) or [Pycharm](https://www.jetbrains.com/pycharm/download/?section=windows).

7. **Fork the repository**. Follow GitHub’s instructions here: https://docs.github.com/en/pull-requests/how-tos/work-with-forks/fork-a-repo

8. To start making changes, continue to our Pull Request Guide (to be linkified)!


## Sister Forks

*This is an advanced guide and is not necessary for contributing to ClanGen. Refer back here only if a special project comes up in which you need to contribute to another developer's fork instead of the main ClanGen repository.*

When working on multiple projects (or if you already have made a personal fork of ClanGen), sometimes it is required to work on multiple forks and branches from different developers (we'll refer to them as "sister forks"). Unfortunately, there is no way to do this directly through GitHub Desktop, but there is a work around. Branching from someone else's fork lets you PR to their fork, rather than the main ClanGen repository, which is helpful for large milestone development.

You can add multiple "sister forks" upstream of your branches, to say have one branch for your mod, another for the ClanGen development version, and another for a secret development project you're contributing to. In order to create branches that are a copy of a "sister fork", you need to add them as another "remote".  If you have your current fork cloned onto your computer, you should already have two remotes - "origin", which is your repository, and "upsteam", which is the repository that you forked (ie, the ClanGen repository). Here is how to add a third (or more):

1. Make sure you have Git installed on your computer. Not just Github desktop. Github Desktop uses a version of git that you can't access via the command line. 
> You can install git on windows using https://git-scm.com/download/win
> You can check if you have git installed by entering the command git --version in terminal
2. Open up the Windows command line (or the mac/Linux equivalent). Ensure that the current working directory is the folder where you cloned your ClanGen fork. 
3. Run this command with the remote url you need for the specific new remote. Here, this example is the git url to add the Lifegen development version as an upstream remote:
```shell
git remote add Lifegen_dev https://github.com/sedgestripe/clangen.git
``` 
You can find this url here on the github page for a fork:
![An image showing where to find the url for a github branch, under the code button](https://media.discordapp.net/attachments/1229932793191206913/1232500116875902987/github_explain.png?ex=6629aeae&is=66285d2e&hm=a7052baf529201613c9441bbeda71cbcaa4c64bcc1bf65b28bd4891af99d719a&=&format=webp&quality=lossless&width=2206&height=1036)
<br> The "Lifegen_dev" bit of the above command names the new remote for your github desktop. Name your remotes informatively.

4. Run git fetch --all to fetch all the info from the new remote. 

Now, when you look at "Other Branches" in Github desktop (if you use Github Desktop), you should see Lifegen's branches listed alongside the "upstream" and "origin" branches.  You can now treat it just like the ClanGen "upstream" branches, and create a copy. 
