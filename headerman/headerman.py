"""
Copyright (c) 2014 Walker Crouse

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""
import sys
import argparse
import glob
import os
import time
import re


# Cache extension headers so we don't need to create them each time
headers = {}

# multiline comment openers for different file extensions
openmulti = {
  "/*": ["java", "c", "cc", "h", "hh", "hpp", "cpp", "php", "js", "m", "cs"],
  '"""': ["py"],
  ": '": ["sh"],
  "=begin": ['rb'],
}

# closers mapped to the openers
closemulti = {
  "/*": " */",
  '"""': '"""',
  ": '": "'",
  "=begin": "=end"
}

# prefixes before each line between opener and closers
prefixes = {
  "/*": " * ",
  '"""': "",
  ": '": "",
  "=begin": ""
}


def main(argv):
  # parse arguments
  parser = argparse.ArgumentParser()
  parser.add_argument("-rm", "--remove", action="store_true", 
                      help="whether the headers should be removed instead of added")
  parser.add_argument("-i", "--input-file", help="file to read header from", dest="header")
  parser.add_argument("-o", "--output-dir", help="directory to search for file in", dest="directory") 
  parser.add_argument("-r", "--recursive", action="store_true", 
                      help="whether to update headers in the directory recursively")
  parser.add_argument("-e", "--extensions", action="append", default=[], help="the extensions to update")

  opts = parser.parse_args(argv)

  # no directory?
  if opts.directory is None:
    print("provide a directory")
    parser.parse_args(["-h"])

  if opts.remove:
    remove_headers(opts.directory, opts.recursive, opts.extensions)
  elif opts.header is None:
    # trying to add headers but has no input
    print("provide an input header")
    parser.parse_args(["-h"])
  else:
    add_headers(opts.header, opts.directory, opts.extensions, opts.recursive)


def add_headers(file, outdir, exts, recursive):
  # get the header
  with open(file) as f:
    header = f.read()
    f.close()
  files = get_files(outdir, exts, recursive)
  # try to write_header to each file
  operate(files, header, write_header)


def remove_headers(dir, recursive, exts):
  files = get_files(dir, exts, recursive)
  operate(files, None, remove_header)


def operate(files, header, op):
  confirm(len(files))
  modified = 0
  for i in xrange(len(files)):
    if op(files[i], header):
      modified += 1
    pcent = float(i+1) / len(files)
    update_progress(pcent*100, files[i])
  print("\n" + str(modified) + " files modified.")


def confirm(amt):
  while True:
    a = raw_input("This operation could potentially modify " + str(amt) + " files. Continue? [y/n]: ")
    if a == 'y':
      break
    elif a == 'n':
      sys.exit()


def write_header(file, header):
  # get the extension
  ext = get_ext(file)
  if ext in headers:
    # check if we have a version cached for this extension
    header = headers[ext]
  else:
    # create header according to the multiline comment in that lang
    newheader = []
    lns = header.split("\n")
    opener, prefix, closer = get_comment_container(ext)
    newheader.append(opener)
    newheader.extend([prefix + ln for ln in lns])
    headers[ext] = header = "\n".join(newheader).rstrip("\r\n") + "\n" + closer

  with open(file, 'r+') as f:
    content = f.read()
    if content.startswith(header):
      # Already has header
      f.close()
      return False
    # Add header + existing content
    f.seek(0, 0)
    f.write(header.rstrip("\r\n") + "\n" + content)
    f.close()
    return True


def remove_header(file, header):
  ext = get_ext(file)
  with open(file, 'r') as f:
    content = f.read()
    opener, prefix, closer = get_comment_container(ext)
    if opener == "" or not content.startswith(opener):
      f.close()
      return False

    begin = 0
    end = content.find(closer)
    if end == -1:
      return False
    end = content.find(closer, len(closer)) if opener == closer else end
    if end == -1:
      return False

    content = content[end+len(closer):].lstrip()
    f.close()

  with open(file, 'w') as f:
    f.write(content)
    f.close()
    return True


def get_ext(file):
  return os.path.splitext(file)[1][1:]


def update_progress(pcent, msg):
  sys.stdout.write("%d%% [%s]        \r" % (pcent, msg))
  sys.stdout.flush()
  time.sleep(0.1)


def get_comment_container(ext):
  for key in openmulti:
    # find opener
    if ext in openmulti[key]:
      # return opener, prefix, then closer
      return key, prefixes[key], closemulti[key]
  return "", "", ""


def get_files(dir, exts, recursive):
  files = []
  exts = ["." + e for e in exts]
  if not recursive:
    if len(exts) > 0:
      for ext in exts:
        files.extend(glob.glob(os.path.join(dir, "*" + ext)))
    else:
      files.extend(glob.glob(os.path.join(dir, "*")))
  else:
    for root, subdirs, fls in os.walk(dir):
      files.extend([os.path.join(root, f) for f in fls])
    if len(exts) > 0:
      files = [f for f in files if f.endswith(tuple(exts))]
  return files


if __name__ == "__main__":
  main(sys.argv[1:])
