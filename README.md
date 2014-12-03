s3-lifecycle-editor
===================

An utility to edit/dump/replace s3 buckets lifecycles.
Tested with python 2.7

## Requirement ##

* Boto >= 2.34 (Might work with older versions, but that's the one it was developed with)

## Help ##
```
%> python s3_lifecycle_editor_runner.py -h
usage: s3_lifecycle_editor_runner.py [-h] -k KEY -i S3_ID -b BUCKET
                                     [-o {edit,dump,replace}] [-f FILE]

Edit bucket lifecycle.
optional arguments:
  -h, --help            show this help message and exit
  -k KEY, --key KEY     AWS key
  -i S3_ID, --id S3_ID  AWS key id
  -b BUCKET, --bucket BUCKET
                        The bucket to edit
  -o {edit,dump,replace}, --operation {edit,dump,replace}
                        The action to perform
  -f FILE, --file FILE  When replacing, define a file
```
