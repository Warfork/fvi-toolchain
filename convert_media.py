#! /usr/bin/env python3

import os
import shutil


renames = {}
reverse_renames = {}
pending = []
unknown = {}


def check_media_or_die():
    if not os.path.isdir('./media'):
        print("Error: There is no `media` subdirectory in this folder")
        print("Hint: You should run this script in your games' directory, where")
        print("      the `media` dir and files like `collections.txt` are located")
        exit(1)


def first_pass():
    KNOWN_ASSETS = ['boxfront', 'box_front', 'boxart2d', 'boxback', 'box_back', 'boxspine', 'box_spine', 'boxside', 'box_side', 'boxfull', 'box_full', 'box', 'cartridge', 'disc', 'cart', 'logo', 'wheel', 'marquee', 'bezel', 'screenmarquee', 'border', 'panel', 'cabinetleft', 'cabinet_left', 'cabinetright', 'cabinet_right', 'tile', 'banner', 'steam', 'steamgrid', 'grid', 'poster', 'flyer', 'background', 'music', 'screenshot', 'video']

    for root, dirs, files in os.walk('./media'):
        for filename in files:
            path = os.path.join(root, filename)
            name, ext = os.path.splitext(filename)

            last_dash = filename.rfind('-')
            if last_dash == -1:
                pending.append(path)
                continue

            name = filename[:last_dash]
            asset = filename[len(name) + 1 : len(filename) - len(ext)].lower()
            if asset not in KNOWN_ASSETS:
                pending.append(path)
                continue

            subfile = filename[last_dash + 1:]
            new_path = os.path.join(root, name, subfile)
            renames[path] = new_path
            reverse_renames[new_path] = path


def second_pass():
    IMAGE_EXTS = ['.png', '.jpg', '.gif']
    VIDEO_EXTS = ['.mp4', '.webm', '.avi']
    AUDIO_EXTS = ['.mp3', '.ogg', '.wav']

    for path in pending:
        name, ext = os.path.splitext(path)

        subfile = ''
        if ext in IMAGE_EXTS:
            subfile = 'box_front'
        elif ext in VIDEO_EXTS:
            subfile = 'video'
        elif ext in AUDIO_EXTS:
            subfile = 'music'

        if not subfile:
            unknown[path] = "Unknown extension ({})".format(ext[1:])
            continue

        new_path = os.path.join(name, subfile + ext)
        if new_path in reverse_renames:
            print("exists")
            unknown[path] = "Collision with another file ({})".format(reverse_renames[new_path])
            continue

        renames[path] = new_path
        reverse_renames[new_path] = path


def print_renames():
    if len(renames) == 0:
        return

    print("The following files will be renamed:")
    for key in renames:
        print("  ", key, " -> ", renames[key])

    print("(total {} files)".format(len(renames)))
    print()


def print_unknown():
    if len(unknown) == 0:
        return

    print("The following files were not recognized and will be ignored:")
    for key in unknown:
        print("  ", key, ":", unknown[key])

    print("(total {} files)".format(len(unknown)))
    print()


def check_renames_or_die():
    if len(renames) == 0:
        print("It seems there are no files to rename automatically, the program will now stop")
        exit(1)


def ask_user_or_die():
    reply = input("Apply these changes? [y/N]: ")
    if reply.lower() not in ['y', 'yes']:
        print("Ok, no changes have been made.")
        exit(0)


def apply_renames():
    for source in renames:
        target = renames[source]
        target_dir = os.path.dirname(target)

        try:
            if not os.path.exists(target_dir):
                os.makedirs(target_dir)

            shutil.move(source, target)
        except OSError as err:
            print("Error: Failed to move `{}` to `{}`: {}".format(source, target, err))

    print("All files renamed, done!")


if __name__ == "__main__":
    check_media_or_die()

    first_pass()
    second_pass()
    print_renames()
    print_unknown()

    check_renames_or_die()
    ask_user_or_die()
    apply_renames()
