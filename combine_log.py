#!/usr/bin/python
__author__ = 'shako'
import os
import argparse
from argparse import ArgumentDefaultsHelpFormatter


class LogCombiner(object):
    def __init__(self):
        self.arg_parser = argparse.ArgumentParser(description='Combine the log file with same keyword in file name.',
                                                  formatter_class=ArgumentDefaultsHelpFormatter)
        self.arg_parser.add_argument('-k', '--keyword', action='store', dest='file_name_keyword', default=None,
                                     help='Specify the keyword of the log files you want to combine.', required=True)
        self.arg_parser.add_argument('-d', '--log-dir', action='store', dest='log_dir', default=None,
                                     help='Specify the log folder.')
        self.arg_parser.add_argument('-o', '--output-name', action='store', dest='output_name', default=None,
                                     help='Specify the combined log name.')
        self.args = self.arg_parser.parse_args()
        if self.args.output_name:
            self.output_name = self.args.output_name
        else:
            self.output_name = self.args.file_name_keyword + '_total'
        if self.args.log_dir:
            self.log_dir = self.args.log_dir
        else:
            self.log_dir = os.getcwd()
        self.output_file_path = os.path.join(self.log_dir, self.output_name)
        if os.path.exists(self.output_file_path):
            os.remove(self.output_file_path)

        self.last_line = None

    def combine_log(self, num):
        file_name = self.args.file_name_keyword + str(num)
        with open(os.path.join(self.log_dir, file_name)) as input_file:
            file_ctnt = input_file.readlines()
            comparing_list = [ctnt.strip() for ctnt in file_ctnt]
            if self.last_line and comparing_list.count(self.last_line) > 0:
                last_index = comparing_list.index(self.last_line)
                write_line_list = [file_ctnt[index] for index in range(len(file_ctnt)) if index > last_index]
            else:
                write_line_list = file_ctnt
            self.last_line = write_line_list[-1].strip()
        with open(self.output_file_path, "a") as output_file:
            output_file.writelines(write_line_list)

    def gen_num_list(self):
        num_list = []
        for name in os.listdir(self.log_dir):
            if name.find(self.args.file_name_keyword) >= 0:
                num_data = name.replace(self.args.file_name_keyword, "")
                if num_data.isdigit():
                    num_list.append(int(num_data))
        return num_list

    def run(self):
        num_list = self.gen_num_list()
        if len(num_list) == 0:
            print "Can't find any file with keyword: [%s] in current dir: [%s]" % (self.args.file_name_keyword, self.log_dir)
        num_list.sort()
        for num in num_list:
            self.combine_log(num)


def main():
    lc_obj = LogCombiner()
    lc_obj.run()

if __name__ == "__main__":
    main()

