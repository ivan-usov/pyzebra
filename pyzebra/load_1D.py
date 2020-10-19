import os
import re
from collections import defaultdict
from decimal import Decimal

import numpy as np

META_VARS_STR = (
    "instrument",
    "title",
    "sample",
    "user",
    "ProposalID",
    "original_filename",
    "date",
    "zebra_mode",
    "proposal",
    "proposal_user",
    "proposal_title",
    "proposal_email",
    "detectorDistance",
)
META_VARS_FLOAT = (
    "omega",
    "mf",
    "2-theta",
    "chi",
    "phi",
    "nu",
    "temp",
    "wavelenght",
    "a",
    "b",
    "c",
    "alpha",
    "beta",
    "gamma",
    "cex1",
    "cex2",
    "mexz",
    "moml",
    "mcvl",
    "momu",
    "mcvu",
    "snv",
    "snh",
    "snvm",
    "snhm",
    "s1vt",
    "s1vb",
    "s1hr",
    "s1hl",
    "s2vt",
    "s2vb",
    "s2hr",
    "s2hl",
)
META_UB_MATRIX = ("ub1j", "ub2j", "ub3j")


def load_1D(filepath):
    """
    Loads *.ccl or *.dat file (Distinguishes them based on last 3 chars in string of filepath
    to add more variables to read, extend the elif list
    the file must include '#data' and number of points in right place to work properly

    :arg filepath
    :returns det_variables
    - dictionary of all detector/scan variables and dictinionary for every measurement.
    Names of these dictionaries are M + measurement number. They include HKL indeces, angles,
    monitors, stepsize and array of counts
    """
    with open(filepath, "r") as infile:
        _, ext = os.path.splitext(filepath)
        det_variables = parse_1D(infile, data_type=ext)

    return det_variables


def parse_1D(fileobj, data_type):
    # read metadata
    metadata = {}
    for line in fileobj:
        if "=" in line:
            variable, value = line.split("=")
            variable = variable.strip()
            if variable in META_VARS_FLOAT:
                metadata[variable] = float(value)
            elif variable in META_VARS_STR:
                metadata[variable] = str(value)[:-1].strip()
            elif variable in META_UB_MATRIX:
                metadata[variable] = re.findall(r"[-+]?\d*\.\d+|\d+", str(value))

        if "#data" in line:
            # this is the end of metadata and the start of data section
            break

    # read data
    measurements = {}
    if data_type == ".ccl":
        decimal = list()
        for line in fileobj:
            counts = []
            measurement_number = int(line.split()[0])
            d = {}
            d["h_index"] = float(line.split()[1])
            decimal.append(bool(Decimal(d["h_index"]) % 1 == 0))
            d["k_index"] = float(line.split()[2])
            decimal.append(bool(Decimal(d["k_index"]) % 1 == 0))
            d["l_index"] = float(line.split()[3])
            decimal.append(bool(Decimal(d["l_index"]) % 1 == 0))
            if metadata["zebra_mode"] == "bi":
                d["twotheta_angle"] = float(line.split()[4])  # gamma
                d["omega_angle"] = float(line.split()[5])  # omega
                d["chi_angle"] = float(line.split()[6])  # nu
                d["phi_angle"] = float(line.split()[7])  # doesnt matter
            elif metadata["zebra_mode"] == "nb":
                d["gamma_angle"] = float(line.split()[4])  # gamma
                d["omega_angle"] = float(line.split()[5])  # omega
                d["nu_angle"] = float(line.split()[6])  # nu
                d["unkwn_angle"] = float(line.split()[7])

            next_line = next(fileobj)
            d["number_of_measurements"] = int(next_line.split()[0])
            d["angle_step"] = float(next_line.split()[1])
            d["monitor"] = float(next_line.split()[2])
            d["temperature"] = float(next_line.split()[3])
            d["mag_field"] = float(next_line.split()[4])
            d["date"] = str(next_line.split()[5])
            d["time"] = str(next_line.split()[6])
            d["scan_type"] = str(next_line.split()[7])
            for i in range(
                int(int(next_line.split()[0]) / 10) + (int(next_line.split()[0]) % 10 > 0)
            ):
                fileline = next(fileobj).split()
                numbers = [int(w) for w in fileline]
                counts = counts + numbers
            d["om"] = np.linspace(
                float(line.split()[5])
                - (int(next_line.split()[0]) / 2) * float(next_line.split()[1]),
                float(line.split()[5])
                + (int(next_line.split()[0]) / 2) * float(next_line.split()[1]),
                int(next_line.split()[0]),
            )
            d["Counts"] = counts
            measurements[measurement_number] = d

            if all(decimal):
                metadata["indices"] = "hkl"
            else:
                metadata["indices"] = "real"

    elif data_type == ".dat":
        # skip the first 2 rows, the third row contans the column names
        next(fileobj)
        next(fileobj)
        col_names = next(fileobj).split()
        data_cols = defaultdict(list)

        for line in fileobj:
            if "END-OF-DATA" in line:
                # this is the end of data
                break

            for name, val in zip(col_names, line.split()):
                data_cols[name].append(float(val))

        data_cols['h_index'] = float(metadata['title'].split()[-3])
        data_cols['k_index'] = float(metadata['title'].split()[-2])
        data_cols['l_index'] = float(metadata['title'].split()[-1])
        data_cols['temperature'] = metadata['temp']
        data_cols['mag_field'] = metadata['mf']
        data_cols['omega_angle'] = metadata['omega']
        data_cols['number_of_measurements'] = len(data_cols['om'])
        data_cols['monitor'] = data_cols['Monitor1'][0]
        measurements["1"] = dict(data_cols)

    else:
        print("Unknown file extention")

    # utility information
    metadata["data_type"] = data_type
    metadata["area_method"] = "fit"

    return {"meta": metadata, "meas": measurements}
