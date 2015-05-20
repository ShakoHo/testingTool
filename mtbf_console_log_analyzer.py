#!/usr/bin/python
__author__ = 'shako'
import os
import argparse
from argparse import ArgumentDefaultsHelpFormatter


class LogAnalyzer(object):
    def __init__(self):
        self.arg_parser = argparse.ArgumentParser(description='Parsing the mtbf console log, and output needed information to stdout.',
                                                  formatter_class=ArgumentDefaultsHelpFormatter)
        self.arg_parser.add_argument('-f', '--log_path', action='store', dest='log_path', default=None,
                                     help='Specify the path of log file you want to analyze.', required=True)

        self.arg_parser.add_argument('-d', '--output-err-detail', action='store_true', dest='output_err_detail', default=None,
                                     help='Output error detail statistics.')

        self.args = self.arg_parser.parse_args()

        self.result = None

    def extract_case_statistics(self):
        tmp_result = {}
        with open(self.args.log_path) as log_file:
            for tmp_line in log_file.readlines():
                if "TEST-START" in tmp_line or "TEST-UNEXPECTED-ERROR" in tmp_line or "TEST-PASS" in tmp_line:
                    case_file_name = tmp_line.strip().split("|")[1].split(" ")[1]
                    case_class_name = tmp_line.strip().split("|")[1].split(" ")[2]
                if "TEST-START" in tmp_line:
                    if case_file_name in tmp_result.keys():
                        tmp_result[case_file_name]["total"] += 1
                    else:
                        tmp_result[case_file_name] = {"class_name": case_class_name, "total": 1, "failed": 0, "pass": 0,
                                                      "failed_reason": {}, "case_pass_total_time": 0}
                if "TEST-UNEXPECTED-ERROR" in tmp_line >= 0:
                    case_error_reason = tmp_line.strip().split("|")[2]
                    if case_file_name in tmp_result.keys():
                        tmp_result[case_file_name]["failed"] += 1
                        if case_error_reason in tmp_result[case_file_name]["failed_reason"].keys():
                            tmp_result[case_file_name]["failed_reason"][case_error_reason] += 1
                        else:
                            tmp_result[case_file_name]["failed_reason"][case_error_reason] = 0
                    else:
                        print "Error!!! this case[%s] can't find TEST-START in the console log!" % case_file_name
                if tmp_line.find("TEST-PASS") >= 0:
                    case_pass_exec_time = int(tmp_line.strip().split("|")[2].split(" ")[2].replace("ms", ""))
                    if case_file_name in tmp_result.keys():
                        tmp_result[case_file_name]["pass"] += 1
                        tmp_result[case_file_name]["case_pass_total_time"] += case_pass_exec_time
                    else:
                        print "Error!!! this case[%s] can't find TEST-START in the console log!" % case_file_name
        self.result = tmp_result

    def output_result_to_stdout(self):
        tmp_total = 0
        tmp_pass = 0
        tmp_fail = 0
        tmp_total_avg_time = 0
        tmp_cnt = 0

        print "%s Output result to stdout %s" %("=".join(["=" for i in range(30)]), "=".join(["=" for i in range(30)]))
        print "%-45s %-7s %-5s %-7s %-8s" % ("case_name", "total", "pass", "failed", "avg_time")
        for case_name in self.result.keys():
            if self.result[case_name]["pass"] > 0:
                tmp_avg_time = self.result[case_name]["case_pass_total_time"] / self.result[case_name]["pass"]
                tmp_cnt += 1
            else:
                tmp_avg_time = 0
            print "%-45s %-7d %-5d %-7d %-8s" % (case_name, self.result[case_name]["total"], self.result[case_name]["pass"],
                                                 self.result[case_name]["failed"], str(tmp_avg_time) + "ms")
            tmp_total += self.result[case_name]["total"]
            tmp_pass += self.result[case_name]["pass"]
            tmp_fail += self.result[case_name]["failed"]
            tmp_total_avg_time += tmp_avg_time
            if self.result[case_name]['failed_reason'].keys() > 0 and self.args.output_err_detail is True:
                print " ".join([" " for i in range(80)])
                for failed_reason in self.result[case_name]['failed_reason'].keys():
                    print "%44s %-80s %s" % ("", failed_reason, self.result[case_name]["failed_reason"][failed_reason])
                print " ".join([" " for i in range(80)])
        print "-".join(["-" for i in range(70)])
        print "%-45s %-7d %-5d %-7d %-8s" % ("Total", tmp_total, tmp_pass, tmp_fail, str(tmp_total_avg_time / tmp_cnt) + "ms")

    def run(self):
        self.extract_case_statistics()
        self.output_result_to_stdout()


def main():
    la_obj = LogAnalyzer()
    la_obj.run()

if __name__ == "__main__":
    main()

