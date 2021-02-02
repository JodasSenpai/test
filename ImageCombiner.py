# -*- coding: utf-8 -*-
"""
Created on Fri Oct 30 12:51:52 2020

@author: Milan
"""

import os
from os import listdir
from os.path import isfile, join

import sys
import shutil
from PIL.Image import Image
from PIL.Image import open
from PIL.Image import new


class ImageCombiner:
    def __init__(self):
        # Map for 48 small parts in images top right position
        self.MAP = [
            [[0, 7000], [1000, 0], [1000, 4000], [1000, 6000], [3000, 2000], [3000, 4000], [3000, 6000], [5000, 6000]],
            [[0, 2000], [0, 4000], [0, 6000], [2000, 2000], [2000, 6000], [4000, 0], [4000, 4000], [4000, 6000],
             [5000, 7000]],
            [[0, 5000], [2000, 1000], [2000, 3000], [2000, 5000], [4000, 1000], [4000, 3000], [4000, 7000], [5000, 0]],
            [[0, 1000], [0, 3000], [2000, 0], [2000, 4000], [2000, 7000], [4000, 2000], [4000, 5000]],
            [[0, 0], [1000, 1000], [1000, 3000], [1000, 7000], [3000, 1000], [3000, 5000], [5000, 1000], [5000, 3000],
             [5000, 5000]],
            [[1000, 2000], [1000, 5000], [3000, 0], [3000, 3000], [3000, 7000], [5000, 2000], [5000, 4000]]]

        self.IMG_CROP_SIZE = 1000  # 1000x1000px

        self.REVERSE_SORT = False
        self.DIR_PATH = 'None'

    def set_dir_path(self, dir_path):
        if (dir_path != ''):
            self.DIR_PATH = dir_path

    def get_dir_path(self):
        return self.DIR_PATH

    def change_sort(self):
        self.REVERSE_SORT = not self.REVERSE_SORT
        print(self.REVERSE_SORT)

    def list_files(self, mypath):
        onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f)) and f.endswith(".jpg")]
        return onlyfiles

    def split_image(self, infile, ind, save_path):
        img = open(infile)

        width, height = img.size
        # move through the map and save only valid images
        for xy in self.MAP[ind]:
            box = (xy[1], xy[0], xy[1] + 1000, xy[0] + 1000)
            img_crop = img.crop(box)

            new_path = os.path.dirname(save_path)
            # test if folder exists
            if not os.path.exists(new_path):
                os.makedirs(new_path)
            # save small image
            new_filename = new_path + ("/{}_{}.jpg".format(xy[0], xy[1]))
            img_crop.save(new_filename)
        return img_crop

    def get_concat_h(self, im1, im2):
        dst = new('RGB', (im1.width + im2.width, im1.height))
        dst.paste(im1, (0, 0))
        dst.paste(im2, (im1.width, 0))
        return dst

    def get_concat_v(self, im1, im2):
        dst = new('RGB', (im1.width, im1.height + im2.height))
        dst.paste(im1, (0, 0))
        dst.paste(im2, (0, im1.height))
        return dst

    def combine_images(self, path):
        # move through map and combine images
        image_list = self.list_files(path)
        image_list.sort()

        fin_img = []
        h_img = []
        for i in range(0, 6):
            im1 = open(path + image_list[i * 8])
            h_img.append(im1)
            for j in range(1, 8):
                im2 = open(path + image_list[i * 8 + j])
                h_img[i] = self.get_concat_h(h_img[i], im2)

        # Concatenate vertically
        fin_img = h_img[0]
        for i in range(1, 6):
            fin_img = self.get_concat_v(fin_img, h_img[i])

        return fin_img

    '''
    1. Set folder with microscope slide
    2. Set focus to manual mode
    3. Take 6 images  with different swich in on position (order is 1 to 6)
    4. Create new folder for these images and set 3 following parameters
    '''

    def run_image_combiner(self):
        if (self.DIR_PATH == 'None'):
            return "No directory chosen"
        for (dirpath, dirnames, filenames) in os.walk(self.DIR_PATH):
            folder_count = len(dirnames)
            files_count = len(filenames)
            break

        focus_folders = []
        if folder_count > 0:
            for (dirpath, dirnames, filenames) in os.walk(self.DIR_PATH):
                focus_folders = dirnames
                break
            end_image_path = self.DIR_PATH + '_koncna'
        elif files_count >= 6:
            focus_folders.append(os.path.basename(self.DIR_PATH))
            end_image_path = os.path.dirname(self.DIR_PATH) + '_koncna'

        else:

            return "Wrong directory"

        out_img_path_folder = '_img/'
        # print(end_image_path)

        if not os.path.exists(end_image_path):
            os.makedirs(end_image_path)

        for folder in focus_folders:
            p = end_image_path + '/' + folder + '_img'
            if not os.path.exists(p):
                os.makedirs(p)

        print(focus_folders)

        for folder in focus_folders:
            focus_folder = folder
            if folder_count > 0:
                image_path = self.DIR_PATH + '/' + folder + '/'
            else:
                image_path = self.DIR_PATH + '/'
            image_out_path = end_image_path + '/' + focus_folder + '_img/'
            print('folder: ' + image_out_path + '........', end=" ")
            #if os.path.isdir(image_out_path):
            #    try:
            #        shutil.rmtree(image_out_path)
            #    except OSError as e:
            #        return ("OSError: %s - %s." % (e.filename, e.strerror))

            # Get images with same focus
            try:
                image_list = self.list_files(image_path)
            except FileNotFoundError as e:
                return ("FileNotFoundError: %s - %s." % (e.filename, e.strerror))

            # Sort images (image 1 is with switch 1)
            if self.REVERSE_SORT == True:
                image_list.sort(reverse=True)
            else:
                image_list.sort()

            # # split all images in 1000x1000
            i = 0
            print(image_list)
            try:
                for i, file_name in enumerate(image_list):
                    self.split_image(image_path + file_name, i, image_out_path)
            except FileNotFoundError as e:
                return ("FileNotFoundError: %s - %s." % (e.filename, e.strerror))

            # combine images in one big image
            try:
                combined = self.combine_images(image_out_path)
            except FileNotFoundError as e:
                return ("FileNotFoundError: %s - %s." % (e.filename, e.strerror))
            # save combined image
            combined.save(image_out_path + "/combined.jpg", quality=100)
            print('succsess')
        return "Succsess"
