""" tests if incident files can be read and transformed into their
    string representation. """

from log_importer.log_import.reader import read_file

def test_read_sample_file_fragment_id():
    """ the correct fragment id is part of the string representation. """

    result = read_file('log_importer/tests/test_files/file_read_test.txt')

    # test if the right fragment_id was detected
    assert result[0] == u'7cf8df3f', "fragment_id %r unexpected" % result[0]

def test_read_sample_file_part_categories():
    result = read_file('log_importer/tests/test_files/file_read_test.txt')

    # test if the right parts were detected
    assert sorted(result[1].keys()) == sorted((u'A', u'B', u'F', u'E', u'H', u'Z')),\
                                    "unexpected keys %r" % result[1].keys()

def test_read_sample_file_part_content_A():
    result = read_file('log_importer/tests/test_files/file_read_test.txt')

    # just test a simple example
    assert result[1]['A'][0] == u"[30/Mar/2015:23:10:38 +0200] VRm7zgr5AlMAAClwIZoAAAAU 10.199.23.1 40889 1.2.3.4 18060\n", "unexpected result %r" % result[1]['A'][0]

def test_should_not_fail_with_file_including_error():
    result = read_file('log_importer/tests/test_files/file_read_with_error.txt')
