## Creating Back-ups

This tab explains how to create back-ups of your saves, whether it's for editing purposes, to have a back-up in case of evil behavior while updating, or to transfer them between devices. 

!!! warning
     When backing-up a specific clan, make sure you are grabbing both the clan folder AND the clan's clan.json file. The Clan will not function without one or the other.

### Windows

1. Open data directory in settings / opendatadirectory.bat in the game folder
2. Right click the saves folder and select "copy"
3. Paste the folder in a safe spot separate from the clangen directory (such as desktop)
4. Rename folder (ex: 0.13 back up)

To apply the back up, take the contents of the duplicated saves folder and copy+paste it into ClanGen's save directory.

If you're replacing the entire save file data, the file path should be clangen/saves/clan, rather than something like clangen/saves/saves/clan. The game only reads a specific file path - it will not find your saves otherwise.

### Macos

1. Open the data directory in settings
2. Right click the saves folder and select "duplicate" (NOT alias, this makes a short cut)
3. Drag the duplicate to a separate location from the clangen directory (such as downloads)
4. Rename folder (ex: 0.13 back up)

To apply the back up, take the contents of the duplicated saves folder and copy+paste it into ClanGen's save directory.

!!! tip
     If unable to open game, open a modded application and open the data directory in its settings, then navigate to clangen's folder

### Chromeos

1. Open data directory in settings or manually navigate to the saves (file path ~.local/share/ClanGen)
2. Open the saves folder, and use ctrl+a and ctrl+c to copy all contents
3. Make a new folder separate from the clangen directory (such as downloads)
4. Rename the newly created folder to "cg saves backup" or similar
5. Paste (ctrl+v) all contents into the created folder

To apply the back up, take the contents of the duplicated saves folder and copy+paste it into ClanGen's save directory.

If you are unable to replace content that's already in the file, delete the content prior to pasting your back-up in.

## Moving Save Data Between Devices

!!! tip
     ClanGen's save data is NOT operating system specific. You can move save data between OS's without problems.

Saves are installed *locally* on your device. ClanGen does not offer a cloud service or anything similar, so if you were to move saves between computers, it would have to be done manually.

Do the following:

1. On your old device, open the ClanGen game > go into settings > click the data directory button at the bottom
2. Compress your saves folder (or the specific save you want to move)
3. You should have a ZIPPED folder named "saves". Please rename it. For example, "0.13 backup"
4. Copy/paste or drag/drop the zipped folder into a storage program or device (USB, google drive, cloud, etc)

```console
- Windows: right click the folder > send to > compressed (zip)
- MacOS: right click the folder > compress
- ChromeOS: right click the folder > select ZIP
```

After step 4, we're now switching to the new device.

5. Once on your new device, make sure ClanGen is installed
6. Go into the storage program/device you used and download the ZIPPED folder you created earlier
7. Extract/decompress the zipped folder
8. Navigate to the ClanGen saves on your old device
9. Open the decompressed folder of your backed-up saves and drag the "saves" folder out to replace the current saves folder within ClanGen's directory

You should now be able to run and play your old saves.

I recommend keeping your compressed zip folder until you know for sure that all your saves are working appropriately. While there hasn't been any bugs due to moving saves between devices, there might be user errors!