#
# s3-lifecycle-edito_runnerr.py
# Mich, 2014-12-02
# Copyright (c) 2014 Datacratic Inc. All rights reserved.
#

import os
import sys
import argparse
from xml.etree import ElementTree
from xml.dom import minidom

from s3_lifecycle_editor import S3LifecycleEditor

def get_bucket_from_file(filename):
    bucket = os.path.basename(filename)
    assert bucket.endswith('.xml'), "Expected a filename ending with .xml"
    return bucket[:-4]

if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description='Edit/dump/replace bucket lifecycle config.')
    parser.add_argument("-k", "--key", help="AWS key", required=True)
    parser.add_argument("-i", "--id", help="AWS key id", required=True,
                        dest="s3_id")
    parser.add_argument("-b", "--bucket", default=None,
                        help="The bucket to edit")
    parser.add_argument("-o", "--operation",
                        help="The action to perform. Default: edit.",
                        choices=["edit", "dump", "replace"], default="edit")
    parser.add_argument("-f", "--file", help="When replacing, define a file",
                        default=None)
    parser.add_argument("--bucket-from-file", default=False,
                        action='store_true',
                        help="Deduces the bucket name from the file name")
    args = parser.parse_args()

    def exit(msg):
        # print parser, message and exit
        parser.print_help()
        print msg
        sys.exit(1)

    if args.operation == "replace":
        if args.file is None:
            exit("When using operation \"replace\" you need to define a file.")
        try:
            open(args.file, 'rt')
        except:
            exit("The file you specified couldn't be opened.")
        if args.bucket is None == args.bucket_from_file:
            exit("When using option replace, you must either specify bucket "
                 "or bucket-from-file")
        if args.bucket_from_file:
            args.bucket = get_bucket_from_file(args.file)

    elif args.file is not None:
        exit("You must not define a file when not in operation replace.")
    elif args.bucket is None:
        exit("You must define bucket")

    editor = S3LifecycleEditor(args.s3_id, args.key, args.bucket)
    if args.operation == "edit":
        editor.edit()
    elif args.operation == "dump":
        cycle = editor.get_cycle_xml()
        print minidom.parseString(ElementTree.tostring(cycle)).toprettyxml()
    elif args.operation == "replace":
        config = ElementTree.parse(args.file)
        editor.update_with_config(config)
    else:
        raise Exception("Unknown operation:" + args.operation)
