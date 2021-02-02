import cv2
import numpy as np
import math
import xml.etree.ElementTree as ET
import os
import sys

class AutoLabel:
    def __init__(self):
        self.DRY_SAMPLE = True
        self.OIL_SAMPLE = False
        self.DIR_PATH = 'None'

    def set_sample(self, number):
        if number == 0:
            self.DRY_SAMPLE = True
            self.OIL_SAMPLE = False
        elif number == 1:
            self.DRY_SAMPLE = False
            self.OIL_SAMPLE = True
        print(self.DRY_SAMPLE)
        print(self.OIL_SAMPLE)
    def set_dir_path(self, dir_path):
        if (dir_path != ''):
            self.DIR_PATH = dir_path

    def get_dir_path(self):
        return self.DIR_PATH

    def new_cords(self, x, y, w, h):
        if (x >= 10):
            x -= 10
        else:
            x = 0
        if (y >= 10):
            y -= 10
        else:
            y = 0
        if (x + w + 20 < 1000):
            w = x + w + 20
        else:
            w = 1000
        if (y + h + 20 < 1000):
            h = y + h + 20
        else:
            h = 1000
        return [x, y, w, h]

    def createXML(self, coordinates, jpg_name, pelod_name):
        boxes = coordinates
        if not os.path.exists(jpg_name):
            print('jpg doesnt exist')

        full_path = os.path.abspath(jpg_name)

        folder_name = full_path.split('\\')[-2]

        file_name = full_path.split('\\')[-1]


        root = ET.fromstring(r"""<annotation>
            <folder>p</folder>
            <filename>0</filename>
            <path>C</path>
            <source>
            <database>Unknown</database>
            </source>
            <size>
            <width>1000</width>
            <height>1000</height>
            <depth>3</depth>
            </size>
            <segmented>0</segmented>
            </annotation>""")

        item = root.findall('folder')
        item[0].text = folder_name

        item = root.findall('filename')
        item[0].text = file_name

        item = root.findall('path')
        item[0].text = full_path

        for a in range(len(boxes)):
            root.append(ET.fromstring(r"""
            <object>
                <name>""" + pelod_name + r"""</name>
                <pose>Unspecified</pose>
                <truncated>0</truncated>
                <difficult>0</difficult>
                <bndbox>""" + r"""
                    <xmin>""" + str(boxes[a][0]) + r"""</xmin>
                    <ymin>""" + str(boxes[a][1]) + r"""</ymin>
                    <xmax>""" + str(boxes[a][2]) + r"""</xmax>
                    <ymax>""" + str(boxes[a][3]) + r"""</ymax>    
                </bndbox>
            </object> """))

        xml_name = jpg_name.replace("jpg", "xml")
        if os.path.exists(xml_name):
            os.remove(xml_name)
        ET.ElementTree(root).write(open(xml_name, 'w'), encoding='unicode')

    def get_oil_coordinates(self, f_path):
        I_name = f_path
        I = cv2.imread(I_name)

        I = cv2.cvtColor(I, cv2.COLOR_BGR2RGB)
        gray = cv2.cvtColor(I, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 200, 290)

        kernel = np.ones((3, 3), np.uint8)

        erosion = cv2.erode(edges, kernel, iterations=1)

        dilation = cv2.dilate(edges, kernel, iterations=1)
        d2 = cv2.erode(dilation, kernel, iterations=1)

        d3 = cv2.dilate(d2, kernel, iterations=3)

        e2 = cv2.erode(d3, kernel, iterations=7)
        ret, labels = cv2.connectedComponents(e2.astype(np.uint8))

        unique, counts = np.unique(labels, return_counts=True)
        numbers = dict(zip(unique, counts))

        for a in numbers:
            if (numbers[a] < 150):
                labels[labels == a] = 0

        labels[labels > 0] = 1
        l = labels.astype(np.uint8)

        contours, hierarchy = cv2.findContours(l, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        boxes = []
        for cnt in contours:
            x, y, w, h = cv2.boundingRect(cnt)
            if ((h) * (w) > 3000):
                x3, y3, w3, h3 = self.new_cords(x, y, w, h)
                small_image = I[y3:h3, x3:w3].copy()
                small_in_big_image = cv2.copyMakeBorder(small_image, 30, 30, 30, 30, cv2.BORDER_CONSTANT)
                gray_smooth = cv2.cvtColor(small_in_big_image, cv2.COLOR_BGR2GRAY)

                gray_smooth = cv2.GaussianBlur(gray_smooth, (5, 5), 0)

                edges_smooth = cv2.Canny(gray_smooth, 20, 60)

                circles = cv2.HoughCircles(edges_smooth, cv2.HOUGH_GRADIENT, 1, 20,
                                           param1=32, param2=27, minRadius=10, maxRadius=30)

                if circles is not None:
                    circles = np.uint16(np.around(circles))
                    for i in circles[0, :]:
                        x2 = (i[0] - i[2])
                        y2 = (i[1] - i[2])

                        x2 = x3 + x2 - 30
                        y2 = y3 + y2 - 30

                        w2 = (i[2] * 2)
                        h2 = (i[2] * 2)
                        x2, y2, w2, h2 = self.new_cords(x2, y2, w2, h2)
                        boxes.append([x2, y2, w2, h2])

            else:
                x, y, w, h = self.new_cords(x, y, w, h)
                boxes.append([x, y, w, h])

        return boxes

    def get_dry_coordinates(self,f_path):
        I_name = f_path
        #print(I_name)

        I = cv2.imread(I_name)
        I = cv2.cvtColor(I, cv2.COLOR_BGR2RGB)
        gray = cv2.bilateralFilter(I, 15, 75, 75)
        gray = cv2.cvtColor(gray, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 130, 180)
        kernel = np.ones((3, 3), np.uint8)

        dilation = cv2.dilate(edges, kernel, iterations=4)
        d2 = cv2.erode(dilation, kernel, iterations=4)

        ret, labels = cv2.connectedComponents(d2.astype(np.uint8))

        unique, counts = np.unique(labels, return_counts=True)
        numbers = dict(zip(unique, counts))

        for a in numbers:
            if (numbers[a] < 150):
                labels[labels == a] = 0

        labels[labels > 0] = 1
        l = labels.astype(np.uint8)

        contours, hierarchy = cv2.findContours(l, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        boxes = []
        for cnt in contours:
            x, y, w, h = cv2.boundingRect(cnt)
            if (((h) * (w)) > 400):
                # continue
                x3, y3, w3, h3 = self.new_cords(x, y, w, h)
                small_image = I[y3:h3, x3:w3].copy()
                small_in_big_image = cv2.copyMakeBorder(small_image, 30, 30, 30, 30, cv2.BORDER_CONSTANT)
                gray_smooth = cv2.cvtColor(small_in_big_image, cv2.COLOR_BGR2GRAY)

                gray_smooth = cv2.bilateralFilter(gray_smooth, 15, 75, 75)

                edges_smooth = cv2.Canny(gray_smooth, 10, 100)

                circles = cv2.HoughCircles(edges_smooth, cv2.HOUGH_GRADIENT, 1, 20,
                                           param1=35, param2=27, minRadius=8, maxRadius=35)

                if circles is not None:
                    circles = np.uint16(np.around(circles))
                    for i in circles[0, :]:
                        x2 = (i[0] - i[2])
                        y2 = (i[1] - i[2])
                        x2 = x3 + x2 - 30
                        y2 = y3 + y2 - 30
                        w2 = (i[2] * 2)
                        h2 = (i[2] * 2)
                        x2, y2, w2, h2 = self.new_cords(x2, y2, w2, h2)
                        boxes.append([x2, y2, w2, h2])
                else:
                    boxes.append([x3, y3, w3, h3])

        return boxes

    def run_auto_label(self, pelod_name):

        if pelod_name == '':
            return "No pelod name"

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

        elif files_count >= 0:
            focus_folders.append(os.path.basename(self.DIR_PATH))


        for focus_folder in focus_folders:

            if folder_count > 0:
                focus_folder = self.DIR_PATH+'/'+focus_folder
            else:
                focus_folder = self.DIR_PATH

            file_names = []
            for (dirpath, dirnames, filenames) in os.walk(focus_folder):
                file_names = filenames
                break
            if len(file_names) <= 0:
                return "no images in directory: "+focus_folder
            for file in file_names:
                if '.jpg' in file:
                    if ('combined' in file):
                        continue

                    image_name = focus_folder+'/'+file

                    if self.DRY_SAMPLE==True:

                        coordinates = self.get_dry_coordinates(image_name)
                    elif self.OIL_SAMPLE==True:
                        coordinates = self.get_oil_coordinates(image_name)
                    self.createXML(coordinates, image_name, pelod_name)
        return "Success"