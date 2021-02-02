import os
import xml.etree.ElementTree as ET
import sys
import math
from random import random
from shutil import copyfile
from zipfile import ZipFile

class RestructAndZip:
    def __init__(self):
        self.DIR_PATH = 'None'

    def set_dir_path(self, dir_path):
        if (dir_path != ''):
            self.DIR_PATH = dir_path

    def get_dir_path(self):
        return self.DIR_PATH

    def addJpgToXmlFile(self, path_to_file):

        tree = ET.parse(path_to_file)

        root = tree.getroot()
        item = root.findall('filename')
        if '.jpg' not in item[0].text:
            item[0].text += '.jpg'

        tree.write(open(path_to_file, 'w'), encoding='unicode')

    def changeXmlFilename(self, path_to_file, filename):
        tree = ET.parse(path_to_file)

        root = tree.getroot()
        item = root.findall('filename')
        item[0].text = filename + '.jpg'

        tree.write(open(path_to_file, 'w'), encoding='unicode')

    def get_all_file_paths(self, directory):
        # initializing empty file paths list
        file_paths = []

        # crawling through directory and subdirectories
        for root, directories, files in os.walk(directory):
            for filename in files:
                # join the two strings in order to form the full filepath.
                filepath = os.path.join(root, filename)
                file_paths.append(filepath)

                # returning all file paths
        return file_paths

    def run_restructure_and_zip(self):

        if not os.path.exists(self.DIR_PATH):
            return 'directory doesnt exist'


        directory_name = self.DIR_PATH
        #focuses_path = './' + directory_name + '/'
        for (dirpath, dirnames, filenames) in os.walk(directory_name):
            focus_folders = dirnames
            break


        if '_koncna' not in directory_name:
            print('Directory doesnt contain word _koncna, check end zip name!')
        end_image_path = directory_name.replace('_koncna', '')
        end_image_path += '_labelirano'
        # check if laberirano dir exists
        if not os.path.exists(end_image_path):
            os.makedirs(end_image_path)

        train_dir = end_image_path + '/' + 'train'
        validation_dir = end_image_path + '/' + 'validation'
        # check if train/validation dir exists
        if not os.path.exists(train_dir):
            os.makedirs(train_dir)

        if not os.path.exists(validation_dir):
            os.makedirs(validation_dir)

        # check if train/validation image and annotation
        train_image = train_dir + '/image'
        train_annotation = train_dir + '/annotation'

        validation_image = validation_dir + '/image'
        validation_annotation = validation_dir + '/annotation'
        if not os.path.exists(train_image):
            os.makedirs(train_image)
        if not os.path.exists(train_annotation):
            os.makedirs(train_annotation)

        if not os.path.exists(validation_image):
            os.makedirs(validation_image)
        if not os.path.exists(validation_annotation):
            os.makedirs(validation_annotation)

        lenght = 0
        for folder in focus_folders:
            # print(folder)
            print('folder: ' + directory_name + '/' + folder + '........', end=" ")
            for (dirpath, dirnames, filenames) in os.walk(directory_name + '/' + folder):
                files = filenames
                break

            for file in files:
                if '.xml' in file:
                    lenght = lenght + 1
                    self.addJpgToXmlFile(directory_name + '/' + folder + '/' + file)
            print('succsess')

        train = round(lenght * (70 / 100))
        validation = round(lenght * (30 / 100))

        for folder in focus_folders:
            print('copy files: ' + directory_name + '/' + folder + '........', end=" ")
            for (dirpath, dirnames, filenames) in os.walk(directory_name + '/' + folder):
                files = filenames
                break
            for file in files:
                if '.xml' in file:
                    name = file.split('.')[0]
                    if ((validation <= 0 or (random() > 0.3)) and train > 0):
                        copyfile(directory_name + '/' + folder + '/' + name + '.xml',
                                 train_annotation + '/' + folder + '_' + name + '.xml')
                        copyfile(directory_name + '/' + folder + '/' + name + '.jpg',
                                 train_image + '/' + folder + '_' + name + '.jpg')
                        self.changeXmlFilename(train_annotation + '/' + folder + '_' + name + '.xml', folder + '_' + name)
                        train = train - 1
                    else:
                        copyfile(directory_name + '/' + folder + '/' + name + '.xml',
                                 validation_annotation + '/' + folder + '_' + name + '.xml')
                        copyfile(directory_name + '/' + folder + '/' + name + '.jpg',
                                 validation_image + '/' + folder + '_' + name + '.jpg')
                        self.changeXmlFilename(validation_annotation + '/' + folder + '_' + name + '.xml',
                                          folder + '_' + name)
                        validation = validation - 1



        lenDirPath = len(end_image_path)
        file_paths = self.get_all_file_paths(end_image_path)

        with ZipFile(end_image_path + '.zip', 'w') as zip:
            # writing each file one by one
            for file in file_paths:
                zip.write(file, file[lenDirPath:])
        return "Succsess"