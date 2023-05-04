import datetime
import os

from procesing import process, config
from moving import move

dst_root = os.path.join(config['root_folder'], config['images_folder'])

move(config['src_root'], dst_root, config['archive_folder'], config['error_folder'], datetime.timedelta(hours=6))
process(config['root_folder'], config['images_folder'], config['thumbnail_folder'], config['qc_folder'])
