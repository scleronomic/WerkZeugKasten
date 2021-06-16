import os
import re
import pickle
import shutil
import platform
import subprocess
import numpy as np

from wzk.printing import print_progress
from wzk.time import get_timestamp

__pickle_extension = '.pkl'
__open_cmd_dict = {'Linux': 'xdg-open',
                   'Darwin': 'open',
                   'Windows': 'start'}


def get_pythonpath():
    try:
        return os.environ['PYTHONPATH'].split(os.pathsep)
    except KeyError:
        return []


def safe_remove(file):
    if os.path.exists(file):
        os.remove(file)
    else:
        pass


def start_open(file):
    open_cmd = __open_cmd_dict[platform.system()]
    subprocess.Popen([f'{open_cmd} {file}'], shell=True)


def save_object2txt(obj, file_name):
    if file_name[-4:] != '.txt' and '.' not in file_name:
        file_name += '.txt'

    with open(file_name, 'w') as f:
        f.write(''.join(["%s: %s\n" % (k, v) for k, v in obj.__dict__.items()]))


def save_pickle(obj, file):
    if file[-4:] != __pickle_extension:
        file += __pickle_extension

    with open(file, 'wb') as f:
        pickle.dump(obj, f)


def load_pickle(file):
    if file[-4:] != __pickle_extension:
        file += __pickle_extension

    with open(file, 'rb') as f:
        ret_di = pickle.load(f)
    return ret_di


def list_files(directory):
    return [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]


def safe_create_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)


def ensure_final_slash(path):
    if path[-1] != '/':
        path += '/'
    return path


def ensure_initial_slash(path):
    if path[0] != '/':
        path = '/' + path
    return path


def ensure_initial_and_final_slash(path):
    path = ensure_initial_slash(path=path)
    path = ensure_final_slash(path=path)
    return path


def ensure_extension_point(ext):
    if ext[0] != '.':
        ext = '.' + ext
    return ext


def ensure_file_extension(*, file, ext):
    ext = ensure_extension_point(ext)

    if file[-len(ext)] != ext:
        idx_dot = file.find('.')
        if idx_dot != -1:
            file = file[:idx_dot]
        file += ext

    return file


def rel2abs_path(path, abs_dir):
    # abs_dir = '/Hello/HowAre/You/'
    # path = 'Hello/HowAre/You/good.txt'
    # path = 'good.txt'

    abs_dir = ensure_initial_slash(path=abs_dir)
    abs_dir = os.path.normpath(path=abs_dir)
    path = ensure_initial_slash(path=path)
    path = os.path.normpath(path=path)

    if abs_dir in path:
        return path
    else:
        return os.path.normpath(abs_dir + path)


# .npz files, maybe own module
def combine_npz_files(*, directory,
                      pattern=None, file_list=None,
                      save=True,
                      verbose=0):

    if file_list is None:
        if pattern is None:
            pattern = re.compile(pattern=r"^[\S]+.npz$")

        assert isinstance(pattern, str)
        assert '.npz' in pattern
        pattern = re.compile(pattern=pattern)

        file_list = list_files(directory=directory)
        file_list = sorted([file for file in file_list if pattern.match(file)])

    new_dict = {}

    for i, file in enumerate(file_list):
        if verbose > 0:
            print_progress(i=i, n=len(file_list))

        data = np.load(directory + file)
        if i == 0:
            for key in data:
                new_dict[key] = data[key]
        else:
            for key in data:
                new_dict[key] = np.concatenate([new_dict[key], data[key]])

    if save:
        np.savez(directory + 'combined_' + get_timestamp() + '.npz', **new_dict)
    return new_dict


def combine_npy_files2(directory, new_name="combined_{new_len}", delete_singles=False, verbose=0):
    directory = os.path.normpath(path=directory)
    file_list = [file for file in os.listdir(directory) if '.npy' in file]
    arr = np.concatenate([np.load(f"{directory}/{file}", allow_pickle=False)
                          for file in file_list], axis=0)
    np.save(file=f"{directory}/{new_name.format(new_len=len(arr))}.npy", arr=arr)


def combine_npy_files(directory, new_name="combined_{new_len}", delete_singles=False, verbose=0):

    directory = os.path.normpath(path=directory)
    file_list = [file for file in os.listdir(directory) if '.npy' in file]
    if verbose:
        print(file_list)

    arr = np.concatenate([np.load(f"{directory}/{file}", allow_pickle=True)[np.newaxis, :]
                          for file in file_list], axis=0)

    if arr.dtype.hasobject:
        arr = [np.concatenate(a) if isinstance(a[0], (tuple, list, np.ndarray)) else a for a in arr.T]
        np.save(file=f"{directory}/{new_name.format(new_len=len(arr[0]))}.npy", arr=arr)
    else:
        arr = arr.reshape([-1] + list(arr.shape)[2:])
        np.save(file=f"{directory}/{new_name.format(new_len=len(arr))}.npy", arr=arr)

    if delete_singles:
        for file in file_list:
            os.remove(file)
    return arr


def clip_npz_file(n_samples, file, save=True):
    directory, file = os.path.split(file)
    file_name, file_extension = os.path.splitext(file)
    assert file_extension == '.npz'

    data = np.load(directory + file)
    new_dict = {}
    for key in data:
        new_dict[key] = data[key][:n_samples]
    if save:
        np.savez(directory + file_name + 'clipped_' + get_timestamp() + file_extension, **new_dict)
    return new_dict


def __read_head_tail(*, file, n=1, squeeze=True, head_or_tail):
    s = os.popen(f"{head_or_tail} -n {n} {file}").read()
    s = s.split('\n')[:-1]

    if squeeze and len(s) == 1:
        s = s[0]

    return s


def read_head(file, n=1, squeeze=True):
    return __read_head_tail(file=file, n=n, squeeze=squeeze, head_or_tail='head')


def read_tail(file, n=1, squeeze=True):
    return __read_head_tail(file=file, n=n, squeeze=squeeze, head_or_tail='tail')


def copy2clipboard(file):
    """
    https://apple.stackexchange.com/questions/15318/using-terminal-to-copy-a-file-to-clipboard
    -> works only for mac!
    """
    subprocess.run(['osascript',
                    '-e',
                    'set the clipboard to POSIX file "{}"'.format(file)])


# shutil.move("path/to/current/file.foo", "path/to/new/destination/for/file.foo")
def split_files_into_dirs(file_list, bool_fun, dir_list, base_dir=None, mode='dry'):

    if base_dir is not None:
        base_dir = os.path.normpath(base_dir)
    else:
        base_dir = ''

    if file_list is None and base_dir:
        file_list = os.listdir(base_dir)
        print(f'Get file_list from {base_dir}')

    for i, d_i in enumerate(dir_list):
        d_i = os.path.normpath(d_i)

        print(f"->{d_i}")

        j = 0
        while j < len(file_list):
            f_j = file_list[j]

            if bool_fun(f_j, i):
                f_j = os.path.normpath(f_j)
                f_j_new = f"{d_i}/{os.path.split(f_j)[-1]}"

                if mode == 'wet':
                    shutil.move(f"{base_dir}/{f_j}", f_j_new)
                print(f_j)

                file_list.pop(j)
            else:
                j += 1

    if mode != 'wet':
        print()
        print("'dry' mode is activated by default, to apply the changes use mode='wet')")


def test_split_files_into_dirs():

    n, m = 20, 3
    from wzk.strings import uuid4
    file_list = [f"{i}{uuid4()}" for i in range(n) for j in range(m)]
    dirs = [f"new_{i}" for i in range(n)]

    split_files_into_dirs(file_list=file_list, dir_list=dirs, mode='dry',
                          bool_fun=lambda s, i: (s[:len(str(i))] == str(i)) and len(s) == 32 + len(str(i)))


def dir_dir2file_array(directory=None, combine_str=True):
    """
    -directory/
    ----subA/
    --------fileA1
    --------fileA2
    --------fileA3
    ----subB/
    --------fileB1
    --------fileB2

    # combined_str = False
    -> [[fileA1, fileA2, fileA3],
        [fileB1, fileB2]]
    # combined_str = True
    -> [[directory/subA/fileA1, directory/subA/fileA2, directory/subA/fileA3],
        [directory/subB/fileB1, directory/subB/fileB2]]
    """

    if directory is None:
        directory = os.getcwd()
    dir_list = sorted([d for d in os.listdir(directory) if d[0] != '.'])

    file_arr = []
    for dir_i in dir_list:
        f_list = sorted([f for f in os.listdir(directory + '/' + dir_i) if f[0] != '.'])

        if combine_str:
            f_list = [f"{directory}/{dir_i}/{f}" for f in f_list]

        file_arr.append(f_list)

    return file_arr


