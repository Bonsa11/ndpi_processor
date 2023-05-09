import os
import shutil
from datetime import datetime as dt


def move(src_root, dst_root, archive_folder, error_folder, run_time):
    init_time = dt.now()
    index = 0
    files = [f for f in os.listdir(src_root) if '.ndpi' in f]
    if len(files) == 0:
        print('found no files to move, moving onto processing images')
        return 0
    else:
        while dt.now() - init_time < run_time:
            # get file
            file = files[index]

            # get paths
            src = os.path.join(src_root, file)
            dst = os.path.join(dst_root, file)
            archive = os.path.join(src_root, archive_folder, file)
            errored = os.path.join(src_root, error_folder, file)

            # check if in old batches
            batches = [fldr for fldr in os.listdir(dst_root) if os.path.isdir(os.path.join(dst_root, fldr))]
            found_img = False
            for batch in batches:
                if os.path.exists(os.path.join(dst_root, batch, file)):
                    try:
                        shutil.move(src, archive)
                        print(f'{file} found in previous batch {batch}')
                        found_img = True
                    except Exception as e:
                        print(f'failed to move {file} to archive: {e}')
                    break

            if not found_img:
                if not os.path.exists(dst):
                    try:
                        shutil.copy(src, dst)
                        shutil.move(src, archive)
                    except Exception as e:
                        print(f'{file} failed : {e}')
                        shutil.move(src, errored)
                else:
                    pass

            index += 1
            if index == len(files):
                break
