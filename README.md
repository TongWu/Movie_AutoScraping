# Movie_AutoScraping

This is a program that can helps to finish the work after downloading the movie to the folder (including the cloud folder mounted by rclone).

The program will do:

1. Delete the file under 500Mb
2. Tidy the movie filename (only -C postfix is supported, more on the way…)
   - Delete the number prefix before the characters
   - Delete [advertisement]
   - Add ‘-’ between characters and numbers
   - Add "-C" if it is not exist
3. Call the [Movie_Data_Capture](https://github.com/yoshiko2/Movie_Data_Capture) program to scrape the metadata and put them on the right place
4. Delete the duplicate file, low resolution in piority
5. GUI for demaon keepliving and config editing (ongoing)
6. Configuration validating and testing (ongoing)
7. Watch modification of the specific folder, run the program periodically (ongoing)

## Quick start

### 1. Download [Movie_Data_Capture](https://github.com/yoshiko2/Movie_Data_Capture) release

Thanks to [@yoshiko2](https://github.com/yoshiko2) for the amazing thought and practise. 

- Download MDC from the [release page]((https://github.com/yoshiko2/Movie_Data_Capture/releases)) and rename the program to `mdc`
- Edit the config.ini file to the way you like

### 2. Run the program

There are few parameters need to fill:

| Parameter             | Required | Description                                                  |
| --------------------- | -------- | ------------------------------------------------------------ |
| -s (\-\-source)       | True     | indicate your folder path consisting your movies need to be organized |
| -dp (\-\-destination) | True     | indicate your folder path that your movies will be organized to |
| -m (\-\-mdc)          | True     | indicate your folder path consisting your mdc program and the config.ini |
| -d (\-\-dryrun)       | False    | show the filename modification result without process it     |

**Example**

```bash
python Movie_Filename_Clean.py -s "/home/tedwu/download" -dp "/home/tedwu/movie" -m "/home/tedwu/program"
```

```bash
python Movie_Filename_Clean.py -s "/home/tedwu/download" -dp "/home/tedwu/movie" -m "/home/tedwu/program" -d
```

