from log_importer.data.objects import Part

import re

def read_from_file(f):
    fragment_id = None
    parts = {}
    current_part = None
    current_part_buffer = []

    for line in f:
        matcher = re.match('--([^-]+)-([ABCDEFGHIJKZ])--', line)

        if matcher:  # beginning of new part

            # fragment_ids must be constant
            if fragment_id:
                assert fragment_id == matcher.group(1)
            else:
                fragment_id = matcher.group(1)

            # the part-category must be unique
            assert matcher.group(2) not in parts

            if current_part:
                # if we're currently capturing a part, store it
                parts[current_part] = current_part_buffer

            # begin a new part
            current_part = matcher.group(2)
            current_part_buffer = []

        else:
            # if we're currently within a part, record the line
            if current_part:
                current_part_buffer.append(line)
            else:
                # otherwise skip it
                continue
    if current_part:
        # if we're currently capturing a part, store it
        parts[current_part] = current_part_buffer

    # without an A part log information is too lacking
    assert 'A' in parts

    return (fragment_id, parts)

# read a file (given by the path parameter) and return it's
# contents in a tupel (fragment_id, {part_category: part})
def read_file(path):

    with open(path, 'r') as f:
        return read_from_file(f)
