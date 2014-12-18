import json
import logging
import os

logger = logging.getLogger('emop')


class EmopPayload(object):

    def __init__(self, input_path, output_path, proc_id):
        self.input_path = input_path
        self.output_path = output_path
        self.proc_id = proc_id
        self.input_filename = os.path.join(self.input_path, "%s.json" % self.proc_id)
        self.output_filename = os.path.join(self.output_path, "%s.json" % self.proc_id)

    def input_exists(self):
        if os.path.isfile(self.input_filename):
            return True
        else:
            return False

    def output_exists(self):
        if os.path.isfile(self.output_filename):
            return True
        else:
            return False

    def save_input(self, data):
        if not os.path.isdir(self.input_path):
            logger.error("payload input path %s does not exist" % self.input_path)
            return None
        if os.path.exists(self.input_filename):
            logger.error("payload input file %s already exists" % self.input_filename)
            return None

        with open(self.input_filename, 'w') as outfile:
            json.dump(data, outfile)

    def save_output(self, data):
        if not os.path.isdir(self.output_path):
            logger.error("payload output path %s does not exist" % self.output_path)
            return None
        if os.path.exists(self.output_filename):
            logger.error("payload output file %s already exists" % self.output_filename)
            return None

        with open(self.output_filename, 'w') as outfile:
            json.dump(data, outfile)

    def load_input(self):
        if not os.path.isfile(self.input_filename):
            logger.error("payload input file %s does not exist" % self.input_filename)
            return None

        with open(self.input_filename) as datafile:
            data = json.load(datafile)

        return data
