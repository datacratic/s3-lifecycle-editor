#
# s3-lifecycle-edito_runnerr.py
# Mich, 2014-12-02
# Copyright (c) 2014 Datacratic Inc. All rights reserved.
#

import sys
import argparse
from xml.etree import ElementTree
from xml.dom import minidom

from s3_lifecycle_editor import S3LifecycleEditor

if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description='Edit/dump/replace bucket lifecycle config.')
    parser.add_argument("-k", "--key", help="AWS key", required=True)
    parser.add_argument("-i", "--id", help="AWS key id", required=True,
                        dest="s3_id")
    parser.add_argument("-b", "--bucket", help="The bucket to edit",
                        required=True)
    parser.add_argument("-o", "--operation",
                        help="The action to perform. Default: edit.",
                        choices=["edit", "dump", "replace"], default="edit")
    parser.add_argument("-f", "--file", help="When replacing, define a file",
                        default=None)
    args = parser.parse_args()

    if args.operation == "replace":
        if args.file is None:
            parser.print_help()
            print "When using operation \"replace\" you need to define a file."
            sys.exit(1)
        try:
            open(args.file, 'rt')
        except:
            parser.print_help()
            print "The file you specified couldn't be opened."
            sys.exit(1)
    elif args.file is not None:
        parser.print_help()
        print "You must not define a file when not in operation replace."
        sys.exit(1)

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
