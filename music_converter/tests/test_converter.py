import os
import unittest

from mock import patch, call

from music_converter.converter import convert_dir, FileAlreadyExistsError, convert_file, NotSupportedError


class ConvertDirTestCase(unittest.TestCase):

    def setUp(self):
        self.isdir_patcher = patch('music_converter.converter.os.path.isdir')
        self.isdir_mock = self.isdir_patcher.start()

        self.listdir_patcher = patch('music_converter.converter.os.listdir')
        self.listdir_mock = self.listdir_patcher.start()

        self.convert_file_patcher = patch('music_converter.converter.convert_file')
        self.convert_file_mock = self.convert_file_patcher.start()

    def tearDown(self):
        self.isdir_patcher.stop()
        self.listdir_patcher.stop()
        self.convert_file_patcher.stop()

    def set_files(self, dirs):
        existing_files = []
        for dir, files in dirs.iteritems():
            for file in files:
                existing_files.append(os.path.join(dir, file))

        self.listdir_mock.side_effect = lambda x: dirs[x]
        self.isdir_mock.side_effect = lambda x: x in dirs.keys()

    def test_convert_dir(self):
        self.set_files({
            '/test/in': ['file1.wav', 'file2.test.wav', 'file3.flac'],
        })

        convert_dir('/test/in', '/test/out')

        self.convert_file_mock.assert_has_calls([
            call('file1.wav', '/test/in', '/test/out', 'sox', None),
            call('file2.test.wav', '/test/in', '/test/out', 'sox', None),
            call('file3.flac', '/test/in', '/test/out', 'sox', None),
        ])

    def test_convert_subdir(self):
        self.set_files({
            '/test/in': ['file1.wav', 'subdir'],
            '/test/in/subdir': ['subfile1.wav', 'subfile2.wav'],
        })

        convert_dir('/test/in', '/test/out', '/usr/bin/sox', 42)

        self.convert_file_mock.assert_has_calls([
            call('file1.wav', '/test/in', '/test/out', '/usr/bin/sox', 42),
            call('subfile1.wav', '/test/in/subdir', '/test/out/subdir', '/usr/bin/sox', 42),
            call('subfile2.wav', '/test/in/subdir', '/test/out/subdir', '/usr/bin/sox', 42),
        ])

    def test_convert_with_custom_command(self):
        self.set_files({
            '/test/in': ['file1.wav', 'subdir'],
            '/test/in/subdir': ['subfile1.wav'],
        })

        convert_dir('/test/in', '/test/out', '/usr/bin/sox')

        self.convert_file_mock.assert_has_calls([
            call('file1.wav', '/test/in', '/test/out', '/usr/bin/sox', None),
            call('subfile1.wav', '/test/in/subdir', '/test/out/subdir', '/usr/bin/sox', None),
        ])

    def test_convert_existing_file(self):
        self.set_files({
            '/test/in': ['file1.wav', 'file2.test.wav', 'file3.flac'],
        })
        self.convert_file_mock.side_effect = FileAlreadyExistsError()

        # is the exception catched?
        convert_dir('/test/in', '/test/out', '/usr/bin/sox', None)

    def test_convert_unsupported_file(self):
        self.set_files({
            '/test/in': ['file1.wav', 'file2.test.wav', 'file3.flac'],
        })
        self.convert_file_mock.side_effect = NotSupportedError()

        # is the exception catched?
        convert_dir('/test/in', '/test/out', '/usr/bin/sox', None)

    def test_convert_dir_with_custom_bitrate(self):
        self.set_files({
            '/test/in': ['file1.wav'],
        })

        convert_dir('/test/in', '/test/out', bitrate=42)

        self.convert_file_mock.assert_has_calls([
            call('file1.wav', '/test/in', '/test/out', 'sox', 42),
        ])


class ConvertFileTestCase(unittest.TestCase):

    def setUp(self):
        self.isdir_patcher = patch('music_converter.converter.os.path.isdir')
        self.isdir_mock = self.isdir_patcher.start()

        self.isfile_patcher = patch('music_converter.converter.os.path.isfile')
        self.isfile_mock = self.isfile_patcher.start()

        self.makedirs_patcher = patch('music_converter.converter.os.makedirs')
        self.makedirs_mock = self.makedirs_patcher.start()

        self.listdir_patcher = patch('music_converter.converter.os.listdir')
        self.listdir_mock = self.listdir_patcher.start()

        self.call_patcher = patch('music_converter.converter.call')
        self.call_mock = self.call_patcher.start()

    def tearDown(self):
        self.isdir_mock = self.isdir_patcher.stop()
        self.isfile_mock = self.isfile_patcher.stop()
        self.makedirs_mock = self.makedirs_patcher.stop()
        self.listdir_mock = self.listdir_patcher.stop()
        self.call_mock = self.call_patcher.stop()

    def set_files(self, dirs):
        existing_files = []
        for dir, files in dirs.iteritems():
            for file in files:
                existing_files.append(os.path.join(dir, file))

        self.listdir_mock.side_effect = lambda x: dirs[x]
        self.isdir_mock.side_effect = lambda x: x in dirs.keys()

    def test_convert_file(self):
        self.isfile_mock.return_value = False

        convert_file('file1.wav', '/test/in', '/test/out')

        self.call_mock.assert_called_once_with(
            ['sox', '/test/in/file1.wav', '-C 320', '/test/out/file1.mp3'])
        self.isfile_mock.assert_called_with('/test/out/file1.mp3')

    def test_convert_file_with_dir_creation(self):
        self.isfile_mock.return_value = False
        self.isdir_mock.return_value = False

        convert_file('file1.wav', '/test/in', '/test/out')

        self.isdir_mock.assert_called_with('/test/out')
        self.makedirs_mock.assert_called_with('/test/out')

    def test_convert_already_existing_file(self):
        self.isfile_mock.return_value = True

        with self.assertRaises(FileAlreadyExistsError):
            convert_file('file1.wav', '/test/in', '/test/out')

    def test_convert_not_supported_extension(self):
        with self.assertRaises(NotSupportedError):
            convert_file('file1.wtf', '/test/in', '/test/out')

    def test_convert_with_custom_command(self):
        self.isfile_mock.return_value = False

        convert_file('file1.wav', '/test/in', '/test/out', '/usr/bin/sox')

        self.call_mock.assert_called_once_with(
            ['/usr/bin/sox', '/test/in/file1.wav', '-C 320', '/test/out/file1.mp3'])

    def test_convert_with_custom_bitrate(self):
        self.isfile_mock.return_value = False

        convert_file('file1.wav', '/test/in', '/test/out', bitrate=42)

        self.call_mock.assert_called_once_with(
            ['sox', '/test/in/file1.wav', '-C 42', '/test/out/file1.mp3'])

if __name__ == '__main__':
    unittest.main()
