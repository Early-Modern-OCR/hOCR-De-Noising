import os
from emop.lib.emop_base import EmopBase
from emop.lib.models.emop_page_result import EmopPageResult
from emop.lib.models.emop_postproc_result import EmopPostprocResult
from emop.lib.utilities import get_temp_dir


class EmopJob(object):

    def __init__(self, job_id, batch_job, font, page, work, settings, scheduler):
        self.id = job_id
        self.output_root_dir = EmopBase.add_prefix(settings.output_path_prefix, settings.ocr_root)
        self.temp_dir = get_temp_dir()
        self.image_path = self.get_image_path(page, work, settings)
        self.batch_job = batch_job
        self.font = font
        self.page = page
        self.work = work
        self.settings = settings
        self.scheduler = scheduler
        self.page_result = EmopPageResult(self.settings)
        self.postproc_result = EmopPostprocResult(self.settings)
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
        self.alto_xml_file = self.add_filename_suffix(self.xml_file, "ALTO")

    def output_dir(self):
        """ Provide the job output directory

        Format is the following:
            /<config.ini output_path_prefix><config.ini ocr_root>/<batch ID>/<work ID>

        Example:
            /dh/data/shared/text-xml/IDHMC-OCR/<batch.id>/<work.id>

        Returns:
            str: Output directory path
        """
        path = os.path.join(self.output_root_dir, str(self.batch_job.id), str(self.work.id))
        return path

    def output_file(self, fmt):
        """ Provide the job output file name

        Format is the following:
            <output_dir>/<page.number>.<fmt>

        Example:
            <output_dir>/<page.number>.<fmt>

        Args:
            fmt (str): File format (extension) for file path

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

        This function generates an image path based on value of image path for a page.
        If a page has no image path then one is generated.

        ECCO image path format:
            eeco_directory/<eeco ID> + <4 digit page ID> + 0.[tif | TIF]
        EEBO image path format:
            eebo_directory/<eebo ID>.000.<0-100>.[tif | TIF]

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
            # EECO
            if work.is_ecco():
                img = "%s/%s%04d0.tif" % (work.ecco_directory, work.ecco_id, page.number)
                image_path = EmopBase.add_prefix(settings.input_path_prefix, img)
                image_path_upcase = image_path.replace(".tif", ".TIF")
                if os.path.isfile(image_path):
                    return image_path
                elif os.path.isfile(image_path_upcase):
                    return image_path_upcase
            # EEBO
            else:
                for i in xrange(101):
                    img = "%s/%05d.000.%03d.tif" % (work.eebo_directory, page.number, i)
                    image_path = EmopBase.add_prefix(settings.input_path_prefix, img)
                    image_path_upcase = image_path.replace(".tif", ".TIF")
                    if os.path.isfile(image_path):
                        return image_path
                    elif os.path.isfile(image_path_upcase):
                        return image_path_upcase
                    else:
                        continue
        return None
