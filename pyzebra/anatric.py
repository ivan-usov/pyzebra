import subprocess
import xml.etree.ElementTree as ET


REFLECTION_PRINTER_FORMATS = (
    "rafin",
    "rafinf",
    "rafin2d",
    "rafin2di",
    "orient",
    "shelx",
    "jana2k",
    "jana2kf",
    "raw",
    "oksana",
)

ALGORITHMS = ("adaptivemaxcog", "adaptivedynamic")


def anatric(config_file):
    subprocess.run(["anatric", config_file], check=True)


class AnatricConfig:
    def __init__(self, filename=None):
        if filename:
            self.load_from_file(filename)

    def load_from_file(self, filename):
        self._tree = ET.parse(filename)
        self._root = self._tree.getroot()

        self._alg_elems = dict()
        for alg in ALGORITHMS:
            self._alg_elems[alg] = ET.Element("Algorithm", attrib={"implementation": alg})

        self._alg_elems[self.algorithm] = self._tree.find("Algorithm")

        alg_elem = self._tree.find("Algorithm")
        if self.algorithm == "adaptivemaxcog":
            self.threshold = float(alg_elem.find("threshold").attrib["value"])
            self.shell = float(alg_elem.find("shell").attrib["value"])
            self.steepness = float(alg_elem.find("steepness").attrib["value"])
            self.duplicateDistance = float(alg_elem.find("duplicateDistance").attrib["value"])
            self.maxequal = float(alg_elem.find("maxequal").attrib["value"])
            # self.apd_window = float(alg_elem.find("window").attrib["value"])

        elif self.algorithm == "adaptivedynamic":
            # self.admi_window = float(alg_elem.find("window").attrib["value"])
            # self.border = float(alg_elem.find("border").attrib["value"])
            # self.minWindow = float(alg_elem.find("minWindow").attrib["value"])
            # self.reflectionFile = float(alg_elem.find("reflectionFile").attrib["value"])
            self.targetMonitor = float(alg_elem.find("targetMonitor").attrib["value"])
            self.smoothSize = float(alg_elem.find("smoothSize").attrib["value"])
            self.loop = float(alg_elem.find("loop").attrib["value"])
            self.minPeakCount = float(alg_elem.find("minPeakCount").attrib["value"])
            # self.displacementCurve = float(alg_elem.find("threshold").attrib["value"])
        else:
            raise ValueError("Unknown processing mode.")

    @property
    def logfile(self):
        return self._tree.find("logfile").attrib["file"]

    @logfile.setter
    def logfile(self, value):
        self._tree.find("logfile").attrib["file"] = value

    @property
    def logfile_verbosity(self):
        return self._tree.find("logfile").attrib["verbosity"]

    @logfile_verbosity.setter
    def logfile_verbosity(self, value):
        self._tree.find("logfile").attrib["verbosity"] = value

    @property
    def filelist_type(self):
        if self._tree.find("FileList") is not None:
            return "TRICS"
        return "SINQ"

    @filelist_type.setter
    def filelist_type(self, value):
        if value == "TRICS":
            tag = "FileList"
        elif value == "SINQ":
            tag = "SinqFileList"
        else:
            raise ValueError("FileList value can only by 'TRICS' or 'SINQ'")

        self._tree.find("FileList").tag = tag

    @property
    def _filelist_elem(self):
        if self.filelist_type == "TRICS":
            filelist_elem = self._tree.find("FileList")
        else:  # SINQ
            filelist_elem = self._tree.find("SinqFileList")

        return filelist_elem

    @property
    def filelist_format(self):
        return self._filelist_elem.attrib["format"]

    @filelist_format.setter
    def filelist_format(self, value):
        self._filelist_elem.attrib["format"] = value

    @property
    def filelist_datapath(self):
        return self._filelist_elem.find("datapath").attrib["value"]

    @filelist_datapath.setter
    def filelist_datapath(self, value):
        self._filelist_elem.find("datapath").attrib["value"] = value

    @property
    def filelist_ranges(self):
        range_vals = self._filelist_elem.find("range").attrib
        return (int(range_vals["start"]), int(range_vals["end"]))

    @filelist_ranges.setter
    def filelist_ranges(self, value):
        range_vals = self._filelist_elem.find("range").attrib
        range_vals["start"] = str(value[0])
        range_vals["end"] = str(value[1])

    @property
    def crystal_sample(self):
        return self._tree.find("crystal").find("Sample").attrib["name"]

    @crystal_sample.setter
    def crystal_sample(self, value):
        self._tree.find("crystal").find("Sample").attrib["name"] = value

    @property
    def crystal_lambda(self):
        elem = self._tree.find("crystal").find("lambda")
        if elem is not None:
            return elem.attrib["value"]
        return None

    @crystal_lambda.setter
    def crystal_lambda(self, value):
        self._tree.find("crystal").find("lambda").attrib["value"] = value

    @property
    def crystal_zeroOM(self):
        elem = self._tree.find("crystal").find("zeroOM")
        if elem is not None:
            return elem.attrib["value"]
        return None

    @crystal_zeroOM.setter
    def crystal_zeroOM(self, value):
        self._tree.find("crystal").find("zeroOM").attrib["value"] = value

    @property
    def crystal_zeroSTT(self):
        elem = self._tree.find("crystal").find("zeroSTT")
        if elem is not None:
            return elem.attrib["value"]
        return None

    @crystal_zeroSTT.setter
    def crystal_zeroSTT(self, value):
        self._tree.find("crystal").find("zeroSTT").attrib["value"] = value

    @property
    def crystal_zeroCHI(self):
        elem = self._tree.find("crystal").find("zeroCHI")
        if elem is not None:
            return elem.attrib["value"]
        return None

    @crystal_zeroCHI.setter
    def crystal_zeroCHI(self, value):
        self._tree.find("crystal").find("zeroCHI").attrib["value"] = value

    @property
    def crystal_UB(self):
        elem = self._tree.find("crystal").find("UB")
        if elem is not None:
            return elem.text
        return None

    @crystal_UB.setter
    def crystal_UB(self, value):
        self._tree.find("crystal").find("UB").text = value

    @property
    def dist1(self):
        return self._tree.find("DataFactory").find("dist1").attrib["value"]

    @dist1.setter
    def dist1(self, value):
        self._tree.find("DataFactory").find("dist1").attrib["value"] = value

    @property
    def reflectionPrinter_format(self):
        return self._tree.find("ReflectionPrinter").attrib["format"]

    @reflectionPrinter_format.setter
    def reflectionPrinter_format(self, value):
        if value not in REFLECTION_PRINTER_FORMATS:
            raise ValueError("Unknown ReflectionPrinter format.")

        self._tree.find("ReflectionPrinter").attrib["format"] = value

    @property
    def algorithm(self):
        return self._tree.find("Algorithm").attrib["implementation"]

    @algorithm.setter
    def algorithm(self, value):
        if value not in ALGORITHMS:
            raise ValueError("Unknown algorithm.")

        self._root.remove(self._tree.find("Algorithm"))
        self._root.append(self._alg_elems[value])

    def save_as(self, filename):
        self._tree.write(filename)
