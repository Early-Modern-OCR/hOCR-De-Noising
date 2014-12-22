import os
from emop.lib.emop_base import EmopBase
from emop.models.emop_page_result import EmopPageResult
from emop.models.emop_postproc_result import EmopPostprocResult


class EmopJob(object):

    def __init__(self, job_id, batch_job, font, page, work, settings):
        self.id = job_id
        self.output_root_dir = EmopBase.add_prefix(settings.output_path_prefix, settings.ocr_root)
        self.image_path = self.get_image_path(page, work, settings)
        self.batch_job = batch_job
        self.font = font
        self.page = page
        self.work = work
        if page.hasGroundTruth():
            self.ground_truth_file = EmopBase.add_prefix(settings.input_path_prefix, page.ground_truth_file)
        else:
            self.ground_truth_file = None
        self.settings = settings
        self.page_result = EmopPageResult()
        self.postproc_result = EmopPostprocResult()
        self.page_result.page_id = self.page.id
        self.page_result.batch_id = self.batch_job.id
        self.postproc_result.page_id = self.page.id
        self.postproc_result.batch_job_id = self.batch_job.id
        self.page_result.juxta_change_index = None
        self.page_result.alt_change_index = None
        # The values below rely on values set above
        self.output_dir = self.output_dir()
        self.txt_file = self.output_file("txt")
        self.xml_file = self.output_file("xml")
        self.hocr_file = self.output_file("hocr")
        self.idhmc_txt_file = self.add_filename_suffix(self.txt_file, "IDHMC")
        self.idhmc_xml_file = self.add_filename_suffix(self.xml_file, "IDHMC")
        self.alto_txt_file = self.add_filename_suffix(self.txt_file, "ALTO")

    def output_dir(self):
        """ Provide the job output directory

        Format is the following:
            /<config.ini output_path_prefix><config.ini ocr_root>/<org_unit>/<work_id>/<batch>

        Example:
            /dh/data/shared/text-xml/IDHMC-OCR/<org_unit>/<work_id>/<batch>

        Returns:
            str: Output directory path
        """
        path = os.path.join(self.output_root_dir, str(self.work.organizational_unit), str(self.work.id), str(self.batch_job.id))
        return path

    def output_file(self, fmt):
        """ Provide the job output file name

        Format is the following:
            /<config.ini output_path_prefix>/<config.ini ocr_root>/<org_unit>/<work_id>/<batch>/<image-file-name>.[txt | xml]

        Example:
            /dh/data/shared/text-xml/IDHMC-OCR/<org_unit>/<work_id>/<batch>/<image-file-name>.[txt | xml]

        Returns:
            str: Output file path
        """
        filename = "%s.%s" % (self.page.number, str(fmt).lower())
        path = os.path.join(self.output_dir, filename)
        return path

    def add_filename_suffix(self, file, suffix):
        """ Add filename suffix

        This function adds a suffix to a filename before the extension

        Example:
        add_filename_suffix('5.xml', 'IDHMC')
            5.xml -> 5_IDHMC.xml

        Args:
            file (str): File name to add suffix
            suffix (str): The suffix to add

        Returns:
            str: The filename with suffix added before extension
        """
        filename, ext = os.path.splitext(file)
        return "%s_%s%s" % (filename, suffix, ext)

    def get_image_path(self, page, work, settings):
        """Determine the full path of an image

        This function may not be necessary but was added to maintain
        compatibility with some of the old Java code

        Args:
            page (EmopPage): EmopPage object
            work (EmopWork): EmopWork object
            settings (EmopSettings): EmopSettings object

        Returns:
            str: Path to the page image
            None is returned if no path could be determined which constitutes an error
        """
        image_path = page.image_path
        if image_path:
            return EmopBase.add_prefix(settings.input_path_prefix, image_path)
        # image path was not provided by API so one will be generated
        else:
            if work.is_ecco():
                # ECCO format: ECCO number + 4 digit page + 0.tif
                img = "%s/%s%04d0.tif" % (work.ecco_directory, work.ecco_number, page.number)
                return img
            else:
                # EEBO format: 00014.000.001.tif where 00014 is the page number.
                # EEBO is a problem because of the last segment before .tif. It is some
                # kind of version info and can vary. Start with 0 and increase til
                # a file is found.
                # TODO
                return None
