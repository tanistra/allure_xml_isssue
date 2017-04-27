import xml.etree.ElementTree
import sys
import csv
import os
import logging
from time import sleep

ISSUES = []
DUPLICATES = []
FORMAT = '%(asctime)-15s %(message)s'
logging.basicConfig(level=logging.INFO, format=FORMAT)
logger = logging.getLogger(__name__)


def get_all_files_name(dir_path):
    files = [f for f in os.listdir(dir_path) if os.path.isfile(os.path.join(dir_path, f))]
    return [x for x in files if x.endswith(".xml")]


def read_xml_test_data(file, path):
    e = xml.etree.ElementTree.parse(os.path.join(path, file)).getroot()

    test_suite = e.find("test-cases")
    test_case = test_suite.findall("test-case")

    for test in test_case:
        name = test.find('name').text
        try:
            desc = test.find('description').text
        except AttributeError:
            logger.warning("Lack of description for test: %s ", name, )
            desc = ''
        for node in test.iter():
            if node.tag == 'label' and node.attrib['name'] == 'issue':
                test_data = {}
                i = node.attrib['value']
                test_data['issues'] = i
                test_data['name'] = name
                test_data['description'] = desc
                ISSUES.append(test_data)


def print_results(results, title):
    print()
    print(20 * '_' + title + 20 * '_')
    for issue in results:
        print(issue['issues'], issue['name'], issue['description'], sep=', ')
    print()


def export_results_to_csv(results, file_name, path=os.path.dirname(__file__)):
    destination_file = os.path.join(path, file_name)
    try:
        if os.path.exists(destination_file):
            os.remove(destination_file)
        csv_output = open(destination_file, 'a', newline='')
        wr = csv.writer(csv_output, delimiter=';')
        for issue in results:
            wr.writerow([issue['issues'], issue['name'], issue['description']])
        logger.info("Output csv created: %s ", destination_file)
    except PermissionError as e:
        logger.error("\n%s \nCannot save results to %s. \nReason: %s. \nClose file and try again. \n%s " % (
            '*' * 20, destination_file, e, '*' * 20))


def main(args):
    xml_files = get_all_files_name(args)
    for file in xml_files:
        read_xml_test_data(file, args)
    logger.info('Issues: logiing...')
    sleep(0.01)
    print_results(ISSUES, 'ISSUES')
    logger.info('Duplicated issues: logging...')
    sleep(0.01)
    export_results_to_csv(ISSUES, 'issues.csv')


if __name__ == "__main__":
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        main('./')
else:
    main(os.path.dirname(__file__))
