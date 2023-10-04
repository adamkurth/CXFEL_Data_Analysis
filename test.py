import sys
sys.path.append("/home/rkirian/work/git/reborn")
import numpy as np
import pyqtgraph as pg
from reborn.fileio.getters import FrameGetter
from reborn.viewers.qtviews import PADView
from reborn.detector import PADGeometry, PADGeometryList
from reborn.dataframe import DataFrame
from reborn.source import Beam
from reborn.simulate.solutions import water_scattering_factor_squared, water_number_density
from reborn.simulate import form_factors
from reborn.const import eV, r_e
from DEigerStream import ZMQStream
from fileWriter import FileWriter


class DummyFrameGetter(FrameGetter):
    def __init__(self):
        print("Initializing DummyFrameGetter")
        detector_shape = (2162, 2068)  # CXLS Dectris Eiger 4M
        pixel_size = 75e-6
        detector_distance = 0.1  # Sample to detector distance
        sample_thickness = 300e-6  # Assuming a sheet of liquid of this thickness
        n_shots = 1  # Number of shots to integrate
        n_photons = 1e8  # Photons per shot
        photon_energy = 8000*eV  # Photon energy
        beam_divergence = 2e-3  # Beam divergence (assuming this limits small-q)
        beam_diameter = 5e-6  # X-ray beam diameter (doesn't really matter for solutions scattering)
        protein_radius = 30e-9  # Radius of our spherical protein (SI units)
        protein_density = 1.34 * 1e3  # Density of spherical protein (g/cm^3, convert to SI kg/m^3)
        protein_concentration = 10  #  Concentration of protein (mg/ml, which is same as SI kg/m^3)
        geom = PADGeometry(distance=detector_distance, shape=detector_shape, pixel_size=pixel_size)
        beam = Beam(photon_energy=photon_energy, diameter_fwhm=beam_diameter, pulse_energy=n_photons*photon_energy)
        mask = geom.beamstop_mask(beam=beam, min_angle=beam_divergence)
        n_water_molecules = sample_thickness * np.pi * (beam.diameter_fwhm/2)**2 * water_number_density()
        m_protein = protein_density * 4 * np.pi * protein_radius ** 3 / 3  # Spherical protein mass
        n = protein_concentration / m_protein  # Number density of spherical proteins
        n_protein_molecules = sample_thickness * np.pi * (beam.diameter_fwhm/2)**2 * n
        q = geom.q_vecs(beam=beam)
        q_mags = geom.q_mags(beam=beam)
        J = beam.photon_number_fluence
        P = geom.polarization_factors(beam=beam)
        SA = geom.solid_angles()
        F_water = water_scattering_factor_squared(q_mags, temperature=300)
        F2_water = F_water**2*n_water_molecules
        F_sphere = form_factors.sphere_form_factor(radius=protein_radius, q_mags=q_mags)
        F_sphere *= (protein_density - 1000)/1000 * 3.346e29  # Protein-water contrast.  Water electron density is 3.35e29.
        F2_sphere = n_protein_molecules * np.abs((F_sphere**2))
        F2 = F2_water + F2_sphere
        I = n_shots * r_e**2 * J * P * SA * F2
        self.I = I
        df = DataFrame()
        df.set_pad_geometry(geom)
        df.set_beam(beam)
        df.set_mask(mask)
        self.df = df
    def get_data(self, frame_number=0):
        df = self.df
        df.set_raw_data(np.random.poisson(self.I))
        return df


class DummyFileWriter():
    def __init__(self):
        pass
    def __decodeImage__(self, data):
        return data



class DectrisStreamFrameGetter(FrameGetter):
    def __init__(self, ip="10.139.1.5", port=9999, debug=1):
        print("Initializing StreamFrameGetter")
        self.geom = PADGeometryList([PADGeometry(shape=(2162, 2068), pixel_size=75e-6, distance=0.1)])
        self.beam = Beam(photon_energy=9500*eV)
        self.fw = FileWriter()
        self.stream = ZMQStream("10.139.1.5", 9999, 1) 
        self.n_frames = 1e8
        self.busy = False
        self.count = 0
    def get_data(self, frame_number=0):
        if self.busy:
            print("Busy...")
            return None
        self.busy = True
        frames = self.stream.receive()
        print(frames)
        self.busy = False
        if frames is None:
            print("No data...")
            return None
        print(len(frames))
        data = self.fw.__decodeImage__(frames)
        print("Data received", data)
        data = np.double(data)
        # try:
        #     data = np.double(data)
        # except:
        #     return None
        dataframe = DataFrame()
        dataframe.set_frame_id(self.count)
        self.count += 1
        dataframe.set_pad_geometry(self.geom)
        dataframe.set_beam(self.beam)
        mask = data < 200
        data[mask == 0] = 0
        dataframe.set_raw_data(data)
        dataframe.set_mask(mask)
        return dataframe


print("Setting up frame getter")
#fg = DummyFrameGetter()
fg = DectrisStreamFrameGetter()
#frame = fg.get_frame(0)
#print(frame)
geom = PADGeometryList([PADGeometry(shape=(2162, 2068), pixel_size=75e-6, distance=0.1)])
pv = PADView(frame_getter=fg, pad_geometry=geom)
pv.set_levels(levels=(0, 1))
pv.show()
pg.mkQApp().exec_()



class H5FrameGetter(FrameGetter):
    def __init__(self, masterpath):
        self.masterpath = masterpath
        self.h5 = h5py.File(masterpath)
        self.n_frames = self.h5["entry/data/data_000001"].shape[0]
        self.shape = self.h5["entry/data/data_000001"].shape[1:]
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


