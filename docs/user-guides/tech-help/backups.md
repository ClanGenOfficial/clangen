## Creating Back-ups

This tab explains how to create backups of your saves, whether it's for editing purposes, to have a backup while updating, or to transfer them between devices. 

!!! warning
     When backing up a specific clan, make sure you are grabbing both the clan folder AND the clan's clan.json file. The Clan will not function without one or the other.

### Windows

1. Open the data directory in settings / opendatadirectory.bat in the game folder
2. Right-click the saves folder and select "copy"
3. Paste the folder in a safe spot separate from the ClanGen directory (such as desktop)
4. Rename folder (ex: 0.13 backup)

To apply the backup, take the contents of the duplicated saves folder and copy+paste it into ClanGen's save directory.

If you're replacing the entire save file data, the file path should be ClanGen/saves/clan, rather than something like ClanGen/saves/saves/clan. The game only reads a specific file path - it will not find your saves otherwise.

### macOS

1. Open the data directory in settings
2. Right-click the saves folder and select "duplicate" (NOT alias. This makes a shortcut)
3. Drag the duplicate to a separate location from the ClanGen directory (such as downloads)
4. Rename folder (ex: 0.13 backup)

To apply the backup, take the contents of the duplicated saves folder and copy+paste it into ClanGen's save directory.

!!! tip
     If unable to open the game, open a modded application and open the data directory in its settings, then navigate to ClanGen's folder

### chromeOS

1. Open data directory in settings or manually navigate to the saves (file path ~/.local/share/ClanGen)
2. Open the saves folder, and use Ctrl+A and Ctrl+C to copy all contents
3. Make a new folder separate from the ClanGen directory (such as downloads)
4. Rename the newly created folder to "cg saves backup" or similar
5. Paste (ctrl+v) all contents into the created folder

To apply the backup, take the contents of the duplicated saves folder and copy+paste it into ClanGen's save directory.

If you are unable to replace content that's already in the file, delete the content prior to pasting your backup in.

## Moving Save Data Between Devices

!!! tip
     ClanGen's save data is NOT operating system specific. You can move save data between OS's without problems.

Saves are installed *locally* on your device. ClanGen does not offer a cloud service or similar. If you were to move saves between computers, it would have to be done manually.

Do the following:

1. On your old device, open the ClanGen game > go into settings > click the data directory button at the bottom
2. Compress your saves folder (or the specific save you want to move)
3. You should have a ZIPPED folder named "saves". Please rename it. For example, "0.13 backup"
4. Copy/paste or drag/drop the zipped folder into a storage program or device (USB, Google Drive, cloud, etc)

After step 4, we're now switching to the new device.

5. Once on your new device, make sure ClanGen is installed
6. Go into the storage program/device you used and download the ZIPPED folder you created earlier
7. Extract/decompress the zipped folder
8. Navigate to the ClanGen saves from your old device
9. Open the decompressed folder of your backed-up saves and drag the "saves" folder out to replace the current saves folder within ClanGen's directory

You should now be able to run and play your old saves.

I recommend keeping your compressed zip folder until you know for sure that all your saves are working appropriately. While there haven't been any bugs due to moving saves between devices, there might be user errors!

---

**What is compressing/zipping? And how do I do it?**

"Compressing" a folder refers to zipping (.zip files) the contents into a smaller, easier-to-manage file that can be decompressed to its original size later. It's ideal to compress folders when using storage devices, as it 1: saves space and 2: guarantees that the files will not be malformed during the storage process. 

- While storage programs such as Google Drive are convenient, they have an unfortunate reputation for either downloading files incorrectly or not downloading them at all when downloading in bulk. Zip files fix that by allowing you to download the zip file, then decompressing it on your system.

Unsure how to compress files/folder on your Operating system?

- Windows: Right-click the folder (make sure it's highlighted), select "Send To", and select Compressed (zipped) folder
- macOS: Right-click the folder and select Compress
- ChromeOS: Right-click the folder and select "Zip Selection"

Unsure how to decompress the files/folder later?

- Windows: Right-click the zipped folder and select "Extract all"
- macOS: Double-click the zipped folder to decompress
- ChromeOS: Chrome does not have a straightforward way to decompress, so double-click the zipped folder to open its contents, highlight all contents using Ctrl + A, then drag all of the contents out of the zipped folder into a regular folder

**When Compressing for ClanGen** it is recommended to *rename* the zipped folder so the main folder is not confused for the actual contents. For example, this is helpful for transferring saves for ClanGen, as you avoid creating a second "saves" folder that would prevent the game from finding your actual saves.
