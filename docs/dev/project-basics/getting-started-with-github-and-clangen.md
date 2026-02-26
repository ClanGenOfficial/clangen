# Getting started with GitHub and ClanGen

## Getting started on Github

1. Make a GitHub account.
2. Set up GitHub Desktop.
    - Install Git. 
    > You can install git on windows using https://git-scm.com/download/win
    > 
    > You can check if you have git installed by entering the command git --version in terminal
    - Install GitHub Desktop.
    - Log into GitHub in GitHub Desktop.
    - (Optional) Git may be set to sign your commits with your email. If you would like your email to remain anonymous, see [Setting your commit email address on GitHub](https://docs.github.com/en/account-and-profile/setting-up-and-managing-your-personal-account-on-github/managing-email-preferences/setting-your-commit-email-address) and [Configuring your global author information](https://docs.github.com/en/desktop/configuring-and-customizing-github-desktop/configuring-git-for-github-desktop)
3. Download an IDE
    - An IDE (Integrated Development Environment) is a code interpreter. These are programs that allow you to view, run, and edit code, they generally provide shortcuts and point out errors to help speed the process. Importantly, that have the code equivalent of Microsoft Word's spellchecker, and help you by highlighting errors. PyCharm or Virtual Studio Code (VSC) are common favorites among the developers of Clangen, but you aren't required to use a specific one. GitHub desktop will automatically try to open the game files within your IDE, and your IDE will also display things like merging conflicts in an easier to understand way.
4. Create a fork of Clangen
    - A fork is a new repository that is a copy of an existing repository. By making a fork, it becomes easier to sync your code with any changes from the main Clangen repository. Changing things on your fork will not affect the main Clangen repository in any way. In fact, unless you are a Senior Contributor, it is _impossible_ for you to accidentally commit to the main Clangen repository.
    - You can create a fork from GitHub Desktop or github web browser or using the terminal. [Github's documentation for doing so is here.](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/working-with-forks/fork-a-repo)
5. Create branches of your own and other people's forks
    - A branch represents a lineage of changes. You should make a new branch to track the changes you make from the base game (the "remote"). You branch _from_ forks, either your own or someone else's. 
    - [This is how you make a branch.](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/creating-and-deleting-branches-within-your-repository)
    - If you are fixing a bug that is also present in the latest release branch (check before you fix the bug), please branch from the latest release branch when fixing your bug. The release branches are named like `release-x.y.z` or `release_x.y.z`, where `x.y.z` are numbers. The latest release is the one where the numbers are the highest. 

When working on multiple projects(or if you already have made a personal fork of clangen), sometimes it is required to work on multiple forks and branches from different developers (we'll refer to them as "sister forks"). Unfortunately, there is no way to do this directly through github desktop, but there is a work around. Branching from someone else's fork lets you PR to their fork, rather than the main Clangen repository, which is very helpful for large milestone development.

You can add multiple "sister forks" upstream of your branches, to say have one branch for your mod, another for the Clangen development version, and another for a secret development project you're contributing to. In order to create branches that are a copy of a "sister fork", you need to add them as another "remote".  If you have your current fork cloned onto your computer, you should already have two remotes - "origin", which is your repository, and "upsteam", which is the repository that you forked (ie, the Clangen repository). Here is how to add a third (or more):

1. Make sure you have Git installed on your computer. Not just Github desktop. Github Desktop uses a version of git that you can't access via the command line. 
> You can install git on windows using https://git-scm.com/download/win
> You can check if you have git installed by entering the command git --version in terminal
2. Open up the Windows command line (or the mac/Linux equivalent). Ensure that the current working directory is the folder where you cloned your Clangen fork. 
3. Run this command with the remote url you need for the specific new remote. Here, this example is the git url to add the Lifegen development version as an upstream remote:
```shell
git remote add Lifegen_dev https://github.com/sedgestripe/clangen.git
``` 
You can find this url here on the github page for a fork:
![An image showing where to find the url for a github branch, under the code button](https://media.discordapp.net/attachments/1229932793191206913/1232500116875902987/github_explain.png?ex=6629aeae&is=66285d2e&hm=a7052baf529201613c9441bbeda71cbcaa4c64bcc1bf65b28bd4891af99d719a&=&format=webp&quality=lossless&width=2206&height=1036)
<br> The "Lifegen_dev" bit of the above command names the new remote for your github desktop. Name your remotes informatively.

4. Run git fetch --all to fetch all the info from the new remote. 

Now, when you look at "Other Branches" in Github desktop (if you use Github Desktop), you should see Lifegen's branches listed alongside the "upstream" and "origin" branches.  You can now treat it just like the Clangen "upstream" branches, and create a copy. 



## WIP, need explanation of how to PR things


    Make your changes!
    Commit your changes and push your changes using GitHub Desktop.

<Write a commit message and push your changes>


## FAQ
What’s the difference between Git, GitHub, and GitHub Desktop?
> Git is the actual software used to manage versions. It has a CLI (command line interface), meaning that to use it normally, you have to type commands into the console on your computer. GitHub is a website that hosts git repositories. GitHub Desktop is a GUI (graphic user interface) for Git that integrates with GitHub. This means that it will allow you to use Git and GitHub by clicking buttons with your mouse.

Why should I use Git?
> You can keep track of any changes you’ve made, it makes it easier to integrate changes, and you have a backup in case something goes wrong with your computer. Also, this is what the CLangen project uses.

Can’t I just upload my files from the GitHub website in my browser?
> You can, but we don’t recommend it. It has some size limits, and it can make it much harder to merge your code later.

What’s the difference between a fork and branch?
> Let’s compare repositories to trees. Imagine that the Clangen repository is one of these trees. The Clangen tree has several branches representing its changes and history. A fork is like a copy of the Clangen tree. This fork has its own branches, which may end up growing differently from the branches on the original tree.
