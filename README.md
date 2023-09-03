# Movie_AutoScraping

This is a program that can helps to finish the work after you download the movie to the folder (including the cloud folder mounted by rclone).

The program will do:

1. Delete the file under 500Mb
2. Tidy the movie filename (with/without subtitle, hacked with/without subtitle)
   - Delete the prefix, e.g., 232GANA-334-C.mp4 -> GANA-334-C.mp4
   - Delete [advertisement], e.g., [233.com]SSNI-334-C.mp4 -> SSNI-334-C.mp4
   - Add ‘-’, e.g., SSNI334C.mp4 -> SSNI-334-C.mp4
   - With subtitle (-c):
     - Delete all characters after the number part
     - Add "-C", e.g., SSNI-334.mp4 -> SSNI-334-C.mp4
   - Without subtitle:
     - Delete all characters after the number part
   - Hacked with subtitle (-uc):
     - Match the pattern and change the tag to -hack-c
   - Hacked without subtitle (-u):
     - Delete all characters after -u but before .extension
     - Change all -u tag to -hack tag
3. Call the [Movie_Data_Capture](https://github.com/yoshiko2/Movie_Data_Capture) program to scrape the metadata and put them on the right place
4. Delete the duplicate file, low resolution in piority
5. GUI for daemon keep-living and config editing (ongoing)
6. Configuration validating and testing (ongoing)
7. Watch modification of the specific folder, run the program periodically (ongoing)

## Quick start

### 1. Download [Movie_Data_Capture](https://github.com/yoshiko2/Movie_Data_Capture) release

Thanks to [@yoshiko2](https://github.com/yoshiko2) for the amazing thought and practice. 

- Download MDC from the [release page]((https://github.com/yoshiko2/Movie_Data_Capture/releases)) and rename the program to `mdc`
- Edit the config.ini file to the way you like
- Move the config.ini into your user .config folder

```bash
mv config.ini ~/.config/mdc/
```

- Or, create the soft link

```bash
mkdir ~/.config/mdc && ln -s config.ini ~/.config/mdc/
```

### 2. Run the program

Create a configuration file named `MAS_config.ini` and fill with the following template:

```ini
[general]
mdc = ./mdc

[sub]
source = ~/source
dest = ~/dest

[no_sub]
source = ~/source2
dest = ~/dest2

[hack_sub]
source = ~/source3
dest = ~/dest3

[hack]
source = ~/source4
dest = ~/dest4
```

There are few parameters need to fill:

| Parameter            | Required | Description                                                  |
|----------------------| -------- | ------------------------------------------------------------ |
| -s (\-\-source)      | Discarded | Indicate your folder path consisting your movies need to be organized |
| -dp (\-\-destination) | Discarded | Indicate your folder path that your movies will be organized to |
| -m (\-\-mdc)         | Discarded | Indicate your folder path consisting your mdc program and the config.ini |
| -d (\-\-dryrun)      | False    | Show the filename modification result without process it    |
| -c (\-\-sub)         | Four of one | Scrape all movies default with subtitle |
| -no (\-\-no_sub) | Four of one | Scrape all movies default with NO subtitle |
| -u (\-\-hack) | Four of one | Scrape all movies default with hacked |
| -uc (\-\-hack_sub) | Four of one | Scrape all movies default with hacked AND subtitle |

**Example**

```bash
python Movie_AutoScraping.py -c
```

```bash
python Movie_AutoScraping.py -uc -d
```

