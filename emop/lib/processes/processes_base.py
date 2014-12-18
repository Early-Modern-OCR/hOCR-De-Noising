import os


class ProcessesBase(object):

    def __init__(self, job):
        self.job = job
        self.output_root_dir = job.output_root_dir
        self.image_path = job.image_path
        self.batch_job = job.batch_job
        self.font = job.font
        self.page = job.page
        self.work = job.work
        self.output_dir = self.output_dir()
        self.txt_file = self.output_file("txt")
        self.xml_file = self.output_file("xml")
        self.hocr_file = self.output_file("hocr")
        self.idhmc_txt_file = self.add_filename_suffix(self.txt_file, "IDHMC")
        self.idhmc_xml_file = self.add_filename_suffix(self.xml_file, "IDHMC")
        self.alto_txt_file = self.add_filename_suffix(self.txt_file, "ALTO")

    def output_dir(self):
        path = os.path.join(self.output_root_dir, str(self.work.organizational_unit), str(self.work.id), str(self.batch_job.id))
        return path

    def output_file(self, fmt):
        filename = "%s.%s" % (self.page.number, str(fmt).lower())
        path = os.path.join(self.output_dir, filename)
        return path

    def add_filename_suffix(self, file, suffix):
        filename, ext = os.path.splitext(file)
        return "%s_%s%s" % (filename, suffix, ext)

    def run(self):
        raise NotImplementedError
