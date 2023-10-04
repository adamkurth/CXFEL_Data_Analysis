import sys
import numpy as np
import h5py
import hdf5plugin
import pyqtgraph as pg
from reborn.fileio.getters import FrameGetter
from reborn.viewers.qtviews import PADView
from reborn.detector import PADGeometry, PADGeometryList
from reborn.dataframe import DataFrame
from reborn.source import Beam
from reborn.const import eV

#datapath = "data/series_3_data_000001.h5"
#masterpath = "data/series_2_master.h5"
#masterpaths = ["data/series_2_master.h5", "data/series_3_master.h5"]

# h5 = h5py.File(datapath)
# data = h5["entry/data/data"]

# h5m = h5py.File(masterpath)
# mdata = print(list(h5m["entry/data"].keys()))
# md = h5m["entry/data/data_000001"][:]

# print(md)

# md[md > 100] = 2

# # pg.image(md)
# pg.image(h5m["entry/data/data_000001"][0, :, :])
# pg.mkQApp().exec_()


class MyFrameGetter(FrameGetter):
    def __init__(self, masterpath):
        self.masterpath = masterpath
        self.h5 = h5py.File(masterpath)
        self.n_frames = self.h5["entry/data/data_000001"].shape[0]
        self.shape = self.h5["entry/data/data_000001"].shape[1:]
        print(self.shape)
        self.geom = PADGeometryList([PADGeometry(shape=self.shape, pixel_size=75e-6, distance=0.1)])
        self.beam = Beam(photon_energy=9500*eV)
    def get_data(self, frame_number=0):
        frame_number = int(frame_number)
        dataframe = DataFrame()
        dataframe.set_pad_geometry(self.geom)
        dataframe.set_beam(self.beam)
        data = np.double(self.h5["entry/data/data_000001"][frame_number,:,:])
        mask = data < 200
        data[mask == 0] = 0
        dataframe.set_raw_data(data)
        dataframe.set_mask(mask)
        return dataframe

masterpath = "series_1_master.h5"
mfg = MyFrameGetter(masterpath)
frame = mfg.get_frame(0)
pv = PADView(frame_getter=mfg, pad_geometry=frame.get_pad_geometry())
pv.set_levels(levels=(0, 1))
pv.show()
pg.mkQApp().exec_()
