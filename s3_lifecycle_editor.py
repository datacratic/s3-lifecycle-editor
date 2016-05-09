#
# s3-lifecycle-editor.py
# Mich, 2014-12-02
# Copyright (c) 2014 Datacratic Inc. All rights reserved.
#

import tempfile
import os
import sys
from functools import partial
from subprocess import call
from xml.etree import ElementTree
from xml.dom import minidom
from boto.exception import S3ResponseError
from boto.s3.connection import S3Connection
from boto.s3.lifecycle import Lifecycle
from boto.s3.lifecycle import Transition

class S3LifecycleEditor(object):
    def reset_xml(self, file_name, cycle_xml):
        f = open(file_name, 'wt')
        to_write = """<?xml version="1.0" ?>
<!--- Example
<LifecycleConfiguration>
    <Rule>
        <ID>sample-rule</ID>
        <Prefix>documents/</Prefix>
        <Status>Enabled</Status>
        <Transition>
            <Days>365</Days>
            <StorageClass>GLACIER</StorageClass>
        </Transition>
        <Expiration>
            <Days>3650</Days>
        </Expiration>
    </Rule>
    <Rule>
        ...
    </Rule>
</LifecycleConfiguration>
-->

"""
        xml_str = minidom.parseString(ElementTree.tostring(cycle_xml)) \
            .toprettyxml()
        to_write += xml_str[xml_str.find("\n") + 1:]
        f.write(to_write)
        f.close()
        return to_write

    def get_parse_error_what_to_do(self):
        reply = None
        while reply not in ["e", "r", "q"]:
            reply = raw_input(
"""Failed to parse XML. What do you want to do?"
[e] Edit
[r] Reset
[q] Quit
Command: """)
        return reply

    def get_transition_from_xml(self, x_transition):
        if x_transition is None:
            return None
        return Transition(days=x_transition.find("Days").text,
                        storage_class=x_transition.find("StorageClass").text)

    def get_rule_kwargs_from_xml(self, x_rule):
        _id = x_rule.find("ID").text
        if _id == "":
            _id = None
        try:
            expiration = int(x_rule.find("Expiration/Days").text)
            if expiration == 0:
                expiration = None
        except AttributeError:
            expiration = None
        return dict(
            id=_id,
            prefix=x_rule.find("Prefix").text,
            status=x_rule.find("Status").text,
            expiration=expiration,
            transition=self.get_transition_from_xml(x_rule.find("Transition")))

    def __init__(self, s3_id, s3_key, bucket):
        conn = S3Connection(s3_id, s3_key)
        self.bucket = conn.get_bucket(bucket)

    def get_cycle_xml(self):
        try:
            cycle = self.bucket.get_lifecycle_config()
            cycle_xml = ElementTree.fromstring(cycle.to_xml())
        except S3ResponseError as exc:
            if exc.error_code == 'NoSuchLifecycleConfiguration':
                cycle_xml = ElementTree.Element("LifecycleConfiguration")
                cycle_xml.text = "\n"
            else:
                raise exc
        return cycle_xml

    def edit(self):
        class FileHolder():
            def __init__(self):
                _, self.path = tempfile.mkstemp()

            def __del__(self):
                os.unlink(self.path)

        file_holder = FileHolder()
        path = file_holder.path
        EDITOR = os.environ.get('EDITOR', 'vim')
        _reset_xml = partial(self.reset_xml, path, self.get_cycle_xml())
        written = _reset_xml()

        while True:
            try:
                call([EDITOR, path])
                config = ElementTree.parse(path)
            except:
                reply = self.get_parse_error_what_to_do()
                if reply == "q":
                    sys.exit(0)
                if reply == "r":
                    written = _reset_xml()
                continue
            break
        with open(path, 'rt') as f:
            if written == f.read():
                print "Nothing changed"
                sys.exit(0)

        self.update_with_config(config)

    def update_with_config(self, config):
        lifecycle = Lifecycle()
        got_rule = False
        for x_rule in config.findall("Rule"):
            got_rule = True
            lifecycle.add_rule(**self.get_rule_kwargs_from_xml(x_rule))

        if got_rule:
            success = self.bucket.configure_lifecycle(lifecycle)
        else:
            success = self.bucket.delete_lifecycle_configuration()
        if not success:
            print "Failed to update rules"
            sys.exit(1)
        print "Successfully updated rule"
