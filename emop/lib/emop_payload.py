import json
import logging
import os
from emop.lib.utilities import mkdirs_exists_ok

logger = logging.getLogger('emop')


class EmopPayload(object):

    def __init__(self, settings, proc_id):
        self.settings = settings
        self.input_path = self.settings.payload_input_path
        self.output_path = self.settings.payload_output_path
        self.completed_output_path = self.settings.payload_completed_path
        self.uploaded_output_path = self.settings.payload_uploaded_path
        self.proc_id = proc_id
        self.input_filename = os.path.join(self.input_path, "%s.json" % self.proc_id)
        self.output_filename = os.path.join(self.output_path, "%s.json" % self.proc_id)
        self.completed_output_filename = os.path.join(self.completed_output_path, "%s.json" % self.proc_id)
        self.uploaded_output_filename = os.path.join(self.uploaded_output_path, "%s.json" % self.proc_id)

    def file_exists(self, filename):
        if os.path.isfile(filename):
            return True
        else:
            return False

    def input_exists(self):
        return self.file_exists(self.input_filename)

    def output_exists(self):
        return self.file_exists(self.output_filename)

    def completed_output_exists(self):
        return self.file_exists(self.completed_output_filename)

    def save(self, data, dirname, filename, overwrite=False):
        if not os.path.isdir(dirname):
            logger.debug("Creating payload directory %s" % dirname)
            mkdirs_exists_ok(dirname)
        if not overwrite and os.path.exists(filename):
            logger.error("payload file %s already exists" % filename)
            return None

        if overwrite:
            logger.debug("Overwriting payload file at %s" % filename)
        else:
            logger.debug("Saving payload to %s" % filename)

        with open(filename, 'w') as outfile:
            json.dump(data, outfile)
        return True

    def load(self, filename):
        if not os.path.isfile(filename):
            logger.error("payload file %s does not exist" % filename)
            return None

        logger.debug("Loading payload from %s" % filename)
        with open(filename) as datafile:
            data = json.load(datafile)

        return data

    def save_input(self, data):
        dirname = self.input_path
        filename = self.input_filename
        save_status = self.save(data=data, dirname=dirname, filename=filename, overwrite=False)
        return save_status

    def save_output(self, data, overwrite=False):
        dirname = self.output_path
        filename = self.output_filename
        save_status = self.save(data=data, dirname=dirname, filename=filename, overwrite=overwrite)
        return save_status

    def save_completed_output(self, data, overwrite=False):
        dirname = self.completed_output_path
        filename = self.completed_output_filename
        save_status = self.save(data=data, dirname=dirname, filename=filename, overwrite=overwrite)
        if save_status and os.path.isfile(self.output_filename):
            logger.debug("Removing payload file %s" % self.output_filename)
            os.remove(self.output_filename)
        return save_status

    def save_uploaded_output(self, data):
        dirname = self.uploaded_output_path
        filename = self.uploaded_output_filename
        save_status = self.save(data=data, dirname=dirname, filename=filename, overwrite=True)
        if save_status:
            if self.completed_output_exists():
                logger.debug("Removing payload file %s" % self.completed_output_filename)
                os.remove(self.completed_output_filename)
            elif self.output_exists():
                logger.debug("Removing payload file %s" % self.output_filename)
                os.remove(self.output_filename)
        return save_status

    def load_input(self):
        filename = self.input_filename
        data = self.load(filename=filename)

        # TODO Need to move or remove input payloads as there will be many after some time
        return data
