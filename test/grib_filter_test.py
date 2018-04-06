import logging
import os
import unittest

from nose.tools import eq_, with_setup

from ece2cmor3 import grib_filter, grib_file, ece2cmorlib, cmor_source, cmor_task, cmor_target

logging.basicConfig(level=logging.DEBUG)

test_data_path = os.path.join(os.path.dirname(__file__), "test_data", "ifs")
tmp_path = os.path.join(os.path.dirname(__file__), "tmp")


def setup():
    grib_file.test_mode = grib_filter_test.test_mode
    if not os.path.exists(tmp_path):
        os.makedirs(tmp_path)


class grib_filter_test(unittest.TestCase):
    test_mode = True

    gg_file = "ICMGGECE3+199001.csv" if test_mode else "ICMGGpl01+199001"
    gg_path = os.path.join(test_data_path, gg_file)
    sh_file = "ICMSHECE3+199001.csv" if test_mode else "ICMSHpl01+199001"
    sh_path = os.path.join(test_data_path, sh_file)

    @staticmethod
    @with_setup(setup)
    def test_initialize():
        grib_filter.initialize(grib_filter_test.gg_path, grib_filter_test.sh_path, tmp_path)
        eq_(grib_filter.varsfreq[(133, 128, grib_file.hybrid_level_code, 9, cmor_source.ifs_grid.point)], 6)
        eq_(grib_filter.varsfreq[(133, 128, grib_file.pressure_level_Pa_code, 85000, cmor_source.ifs_grid.point)], 6)
        eq_(grib_filter.varsfreq[(164, 128, grib_file.surface_level_code, 0, cmor_source.ifs_grid.point)], 3)

    @staticmethod
    @with_setup(setup)
    def test_validate_tasks():
        grib_filter.initialize(grib_filter_test.gg_path, grib_filter_test.sh_path, tmp_path)
        ece2cmorlib.initialize()
        tgt1 = ece2cmorlib.get_cmor_target("clwvi", "CFday")
        src1 = cmor_source.ifs_source.read("79.128")
        tsk1 = cmor_task.cmor_task(src1, tgt1)
        tgt2 = ece2cmorlib.get_cmor_target("ua", "Amon")
        src2 = cmor_source.ifs_source.read("131.128")
        tsk2 = cmor_task.cmor_task(src2, tgt2)
        valid_tasks = grib_filter.validate_tasks([tsk1, tsk2])
        eq_(valid_tasks, [tsk1, tsk2])
        key1 = (79, 128, grib_file.surface_level_code, 0, cmor_source.ifs_grid.point)
        key2 = (131, 128, grib_file.pressure_level_Pa_code, 92500., cmor_source.ifs_grid.spec)
        eq_(grib_filter.varstasks[key1], [tsk1])
        eq_(grib_filter.varstasks[key2], [tsk2])
        aname, ltype, plevs = cmor_target.get_z_axis(tgt2)
        levs = sorted([float(p) for p in plevs])
        levcheck = sorted([k[3] for k in grib_filter.varstasks if k[0] == 131])
        eq_(levs, levcheck)
