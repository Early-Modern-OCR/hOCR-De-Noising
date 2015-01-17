import glob
import json
import logging
import os
from emop.lib.emop_base import EmopBase
from emop.lib.emop_payload import EmopPayload

logger = logging.getLogger('emop')


class EmopUpload(EmopBase):

    def __init__(self, config_path):
        super(self.__class__, self).__init__(config_path)

    def upload(self, data):
        # TODO Validate data?
        logger.debug("Payload: \n%s" % json.dumps(data, sort_keys=True, indent=4))
        upload_request = self.emop_api.put_request("/api/batch_jobs/upload_results", data)
        if not upload_request:
            logger.error("EmopUpload: Failed to upload results")
            return None

        logger.debug("Returned data: \n%s" % json.dumps(upload_request, sort_keys=True, indent=4))
        return upload_request

    def upload_proc_id(self, proc_id):
        payload = EmopPayload(self.settings, proc_id)
        if payload.completed_output_exists():
            filename = payload.completed_output_filename
        elif payload.output_exists():
            filename = payload.output_filename
        else:
            logger.error("EmopUpload: Could not find payload file for proc_id %s" % proc_id)
            return False

        upload_status = self.upload_file(filename=filename)
        return upload_status

    def upload_file(self, filename):
        filename_path = os.path.abspath(filename)
        file_basename = os.path.basename(filename_path)
        proc_id, file_ext = os.path.splitext(file_basename)
        payload = EmopPayload(self.settings, proc_id)
        if not os.path.isfile(filename_path):
            logger.error("EmopUpload: Could not find file %s" % filename_path)
            return None

        with open(filename_path) as datafile:
            data = json.load(datafile)

        uploaded = self.upload(data)
        if uploaded:
            logger.info("Successfully uploaded payload file %s" % filename_path)
            payload.save_uploaded_output(data)
            return True
        else:
            return False

    def upload_dir(self, dirname):
        dirname_path = os.path.abspath(dirname)
        if not os.path.isdir(dirname_path):
            logger.error("EmopUpload: Could not find directory %s" % dirname_path)
            return False

        files_glob = os.path.join(dirname_path, "*.json")
        files = glob.glob(files_glob)
        for file in files:
            self.upload_file(file)

        # TODO handle failure of individual files
        return True
