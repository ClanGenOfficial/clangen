# Installing Application

"Application" refers to the packaged version of ClanGen that most people are familiar with. It comes with an executable (.exe, .app) and is relatively easy to install.

Yes, this guide can also work and apply with **up-to-date** mods. You just have to take the initiative to change some details to reflect the mod you're installing. Make sure to read the instructions carefully.

---

## QNA

A brief QNA for questions that might want to be answered before the download process.

### Can the application version be modded?

It depends on what mod you want to add. If the mod in question is an add-on that requires you to install and/or modify .py files, **no**.

The application does not allow the player access to the core coding of the game. You will need the source version for that (see the installing UV tab).

### Do the application versions provide downloads for older operating systems?

The application is based on the GitHub releases ClanGen is able to create. If GitHub drops support for an operating system, such as Windows 32-bit and Linux 2.31, then ClanGen will also no longer provide it.

Since the application versions are operating system specific, if you don't see your OS, you can attempt to install the source version as an alternative (see the installing UV tab).

### Anti-Virus

ClanGen does not offer support for issues surrounding anti-virus due to security issues. They do not want to accidentally help with potential malicious downloads (essentially).

If you are concerned with anti-virus preventing ClanGen from being downloaded or opened, ClanGen is an open source project on GitHub that has all its files and actions viewable. The game has an unregistered exe and an inactive built-in updater, so it's frequently auto-flagged as malicious when it's not.

Ultimately, it is up to the player to decide if they would like to continue with installing ClanGen.

### Can I store my ClanGen on OneDrive or another storage program?

It is not recommended. Keep ClanGen on your device's disk.

Keeping ClanGen in OneDrive or similar can make you run into errors, weird game behaviour involving the save files, or saving issues. It can also be difficult once multiple versions of ClanGen are being stored in OneDrive or similar, as there can be potential file confusion.

### Decompressing/Unzipping

Unsure how to decompress the files/folder?

- Windows: Right-click the zipped folder and select "Extract all"
- macOS: Double-click the zipped folder to decompress
- ChromeOS: Chrome does not have a straightforward way to decompress, so double-click the zipped folder to open its contents, highlight all contents using Ctrl + A, then drag all of the contents out of the zipped folder into a regular folder

Unable to decompress a zip due to the program asking for pay? Delete the program you currently have and download [7zip](https://7-zip.org/download.html) or another free alternative. You should not have to PAY to unzip something.

### Terminology

If you are unsure of the terms I'm using and how they apply to installing the game, please check here for definitions! Apologies if I miss something.

**Operating system**: The device's system, such as Windows, macOS, chromeOS, or Linux.

- If you do not know what operating system you're using, you can find it in your device's "system" settings.

**Source**: A version of ClanGen that gives you access to ClanGen's core coding, rather than it being compressed into an easy-to-use launcher.

- Source can be BOTH stable and development. Source =/= development

**Application**: Application refers to the exe install that has all the core coding compressed into the application launcher.

**Terminal**: Terminals are a text-based interface used to effectively communicate with a computer's operating system, allowing the user to input commands and execute tasks.

---

## chromeOS/Linux

!!! warning
     To install ClanGen on chromeOS, you need to have Linux installed and working on your chromeOS device before you can continue. Here is a [help page](https://support.google.com/chromebook/answer/9145439?hl=en#:~:text=your%20administrator.-,Turn%20on%20Linux,-Linux%20is%20off) if you need instructions on how to set up Linux.

The only download locations for ClanGen are:
[clangen.io](https://clangen.io/download), [itch.io](https://sablesteel.itch.io/clan-gen-fan-edit), and [GitHub Releases](https://github.com/ClanGenOfficial/clangen/releases). DO NOT download elsewhere, or trust another user to give you a zip of the ClanGen download.

To begin, navigate to the clangen.io download page provided above. If clangen.io doesn't work for you, you can also theoretically use itch.io or GitHub Releases.

On the download page, you're going to see a ChromeOS or Linux download option with a green download button. Right-click the green download button and select "copy link address". Paste this somewhere to save it for later.

- You should have something similar to `https://clangen.io/api/v1/Update/Channels/stable/Releases/Latest/Artifacts/linux2.35`

Make sure you have access to `Linux Files` before you proceed.

### Downloading

!!! tip
     If you downloaded ClanGen previously, use the command `rm -r Clangen` first to get rid of the previous install. Your ClanGen saves should transfer to the new download automatically, but if you're unsure, follow the backups tab.

Open the Linux terminal/terminal app.

Type `wget` into the terminal, and paste the previous link address from before after the command. You should be left with something similar to:

```console
wget https://clangen.io/api/v1/Update/Channels/stable/Releases/Latest/Artifacts/linux2.35
```

Once the command is done "saving to: linux2.35" without an error, proceed with the next command.

```console
tar -xf linux2.35
```

This is extracting the ClanGen game the terminal downloaded. It is normal for nothing to show in the terminal once the command is sent.

---

Open your file manager and proceed to your Linux files. You will see a newly generated `Clangen` folder and a `linux2.35` file present in the Linux files. Delete the `linux2.35` file.

- The `Clangen` folder is your games folder, and you can rename this folder if you're installing a mod, development, or would like multiple ClanGen versions downloaded. **Renaming the folder will change your run command.**

### Run Command

After you check on your Linux files, open or go back to your terminal. Type in the following command:

```console
./Clangen/Clangen
```

If you renamed the folder, the first Clangen as shown in the example should reflect the folder you renamed. If you renamed it to ClangenDev, for example, `./ClangenDev/Clangen`. Capitalization is important for this command.

---

## Windows

The only download locations for ClanGen are: [clangen.io](https://clangen.io/download), [itch.io](https://sablesteel.itch.io/clan-gen-fan-edit), and [GitHub Releases](https://github.com/ClanGenOfficial/clangen/releases). DO NOT download elsewhere, or trust another user to give you a zip of the ClanGen download.

### Downloading

Navigate to the clangen.io download page listed above and download the Windows option reflecting your device's operating system.

- Windows 10+: Windows 10 and newer
- Windows 64: intended for Windows 7/8 devices, but newer Windows devices can also install this

Once the download is finalized, open your file explorer and open the downloads folder on your device.

- If ClanGen was downloaded on OneDrive, please move it to the device's actual disk

You should see a newly downloaded ZIPPED folder of ClanGen in your downloads. Right-click the zipped folder and select "extract all". If it asks if you'd like to replace, select Skip All.

---

### Running

After using the extract option, you should notice a new, decompressed folder was created. Open it.

You should have a ClanGen folder inside that you'll open to access the clangen.exe. Double-click to run it.

- If you do not see one, or it's not allowing you to open it due to security, you need to play with your antivirus. ClanGen does not help with antivirus due to security issues
- If you run it and a Windows screen pops up saying ClanGen is an unknown publisher, click the "read more" button, then the "run anyway" button

You can now delete the zipped ClanGen folder in your downloads. I'd recommend renaming the main game folder to "clangen 0.13.3", "clangendev", etc to avoid future confusion if you plan on downloading multiple ClanGen versions.

## macOS

The only download locations for ClanGen are: [clangen.io](https://clangen.io/download), [itch.io](https://sablesteel.itch.io/clan-gen-fan-edit), and [GitHub Releases](https://github.com/ClanGenOfficial/clangen/releases). DO NOT download elsewhere, or trust another user to give you a zip of the ClanGen download.

### Downloading

Navigate to the clangen.io download page listed above and download the macOS option.

When the download is done, open your Finder > Downloads folder, and double-click the zipped dmg file that was downloaded from the website. This will decompress the zip and generate a regular dmg file.

Once the dmg file is generated, double-click or right-click > select Open to run the file.

A pop-up will appear. Drag the ClanGen icon to the left-hand side to the applications icon to the right-hand side. This will download and place the actual application file in your "Applications".

---

### Running

Navigate to your "Applications", find the "ClanGen" application, and double-click the file to run the game. This application can be renamed, so feel free to rename it if you intend to download more ClanGen versions in the future.

- If you get a pop-up "Apple cannot verify the file", instead of double-clicking, right-click > run. Try this multiple times.
- If it still doesn't work, go into your system preferences > security > clangen. Select run anyway

---