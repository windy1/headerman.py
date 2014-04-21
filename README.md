# headerman

Manage your source file headers easily. This only manages comments in the absolute beggining of files, no need to worry
about other comments being overwritten. Useful for license changes or updating files with a license header.

## Example

### Add headers to files in the directory "src" with "java" and "py" file extensions

`python headerman.py -i HEADER.txt -o src -e java -e py`

Add the `-r` flag to walk the directory recursively

### Remove headers from all files recursively in the "src" directory

`python headerman.py -rm -o src -r`

`python headerman.py -h` for full help text
