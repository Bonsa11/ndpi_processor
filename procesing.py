import os
import yaml

with open("./config.yaml", "r") as stream:
    try:
        config = (yaml.safe_load(stream))
    except yaml.YAMLError as exc:
        print(exc)

if os.name == 'nt' and hasattr(os, 'add_dll_directory'):
    # Python >= 3.8 on Windows
    with os.add_dll_directory(config['OPENSLIDE_PATH']):
        from openslide import open_slide
else:
    from openslide import open_slide

from datetime import datetime as dt
from shutil import move


def process(root_folder, images_folder, thumbnail_folder, qc_folder):
    # check folders exist
    tests = {'root': os.path.exists(root_folder),
             'images': os.path.exists(os.path.join(root_folder, images_folder)),
             'qc': os.path.exists(os.path.join(root_folder, qc_folder)),
             'thumbnails': os.path.exists(os.path.join(root_folder, thumbnail_folder))}

    if all(tests.values()):
        print('all paths found!')
    else:
        print('not all paths were found')
        for k in tests.keys():
            if not tests[k]:
                print(f'ndpi {k} folder found')

    # get next batch number
    imgs = [f for f in os.listdir(os.path.join(root_folder, images_folder)) if
            os.path.isfile(os.path.join(root_folder, images_folder, f))]
    img_batches = [imgs[x:x + 30] for x in range(0, len(imgs), 30)]
    fldrs = [fldr for fldr in os.listdir(os.path.join(root_folder, images_folder)) if
             os.path.isdir(os.path.join(root_folder, images_folder, fldr)) and 'batch_']
    last_batch = int(sorted(fldrs)[-1][6:])

    for img_batch in img_batches:
        # create new batch folders
        last_batch += 1
        new_folder = f'batch_{last_batch}'
        os.makedirs(os.path.join(root_folder, images_folder, new_folder))
        os.makedirs(os.path.join(root_folder, qc_folder, new_folder))
        os.makedirs(os.path.join(root_folder, thumbnail_folder, new_folder))
        # move a batch of images into that folder
        for img in img_batch:
            src = os.path.join(root_folder, images_folder, img)
            dst = os.path.join(root_folder, images_folder, new_folder, img)
            move(src, dst)

    # loop through images in batch folders and produce thumbnail and qc image for each image
    for batch in [fldr for fldr in os.listdir(os.path.join(root_folder, images_folder)) if
                  os.path.isdir(os.path.join(root_folder, images_folder, fldr)) and 'batch_']:

        print(f'processing batch {batch}')

        for file_name in os.listdir(os.path.join(root_folder, images_folder, batch)):

            print(f'\t processing image {file_name}')
            init_time = dt.now()

            # defining paths for all images
            file_path = os.path.join(root_folder, images_folder, batch, file_name)
            thumbnail_path = os.path.join(root_folder, thumbnail_folder, batch,
                                          f"{'_'.join(file_name.split('.')[:-1])}_thumbnail.png")
            macro_path = os.path.join(root_folder, qc_folder, batch, f"{'_'.join(file_name.split('.')[:-1])}_macro.png")

            # check if the paths exists
            if os.path.exists(thumbnail_path):
                create_thumb = False
                print(f'\t\t thumbnail for {file_name} already exists')
            else:
                create_thumb = True

            if os.path.exists(macro_path):
                create_macro = False
                print(f'\t\t macro image for {file_name} already exists')
            else:
                create_macro = True

            if create_macro or create_thumb:
                try:
                    with open_slide(file_path) as ndpi:
                        if create_thumb:
                            level = ndpi.level_count - 1
                            size = ndpi.level_dimensions[level]
                            img = ndpi.read_region((0, 0), level, size)
                            img.save(thumbnail_path)

                        if create_macro:
                            img = ndpi.associated_images['macro'].rotate(270, expand=True)
                            img.thumbnail((800, 800))  # setting max size
                            img.save(macro_path)
                except Exception as e:
                    print(f' !!! {file_name} failed to process : {e} !!!')
                    move(file_path, os.path.join(os.path.join(root_folder, images_folder, 'errored_images', file_name)))

            print(f'\t\t processing took {dt.now() - init_time}')
