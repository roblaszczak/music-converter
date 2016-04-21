import logging
import os
from subprocess import call

SUPPORTED_EXTENSIONS = ('wav', 'flac')
OUT_EXTENSION = 'mp3'

DEFAULT_BITRATE = 320

logger = logging.getLogger('converter')


def convert_dir(in_dir, out_dir, sox_cmd='sox', bitrate=None):
    files = os.listdir(in_dir)
    logger.debug('files in %(dir)s: %(files)s', {'dir': in_dir, 'files': files})

    for file in files:
        file_path = os.path.join(in_dir, file)
        out_path = os.path.join(out_dir, file)

        if os.path.isdir(file_path):
            convert_dir(file_path, out_path, sox_cmd, bitrate)
        else:
            try:
                convert_file(file, in_dir, out_dir, sox_cmd, bitrate)
            except FileAlreadyExistsError as e:
                logger.info(e.message)
            except NotSupportedError as e:
                logger.info(e.message)


def convert_file(file, in_dir, out_dir, sox_cmd='sox', bitrate=None):
    logger.debug('converting %(file)s, in dir: %(in_dir)s out dir: %(out_dir)s', {
        'file': file,
        'in_dir': in_dir,
        'out_dir': out_dir,
    })

    if bitrate is None:
        bitrate = DEFAULT_BITRATE

    if not file.endswith(SUPPORTED_EXTENSIONS):
        raise NotSupportedError('extension of {} is not supported'.format(file))

    out_file_name = file
    for ext in SUPPORTED_EXTENSIONS:
        if out_file_name.endswith(ext):
            out_file_name = out_file_name.replace(ext, OUT_EXTENSION)

    in_file_path = os.path.join(in_dir, file)
    out_file_path = os.path.join(out_dir, out_file_name)

    if os.path.isfile(out_file_path):
        raise FileAlreadyExistsError('file {} already exists'.format(out_file_path))

    if not os.path.isdir(out_dir):
        os.makedirs(out_dir)

    # todo - progress bar
    cmd = [sox_cmd, in_file_path, '-C {}'.format(bitrate), out_file_path]
    logger.debug('running %(cmd)s', {'cmd': cmd})
    call(cmd)


class FileAlreadyExistsError(Exception):
    pass


class NotSupportedError(Exception):
    pass
