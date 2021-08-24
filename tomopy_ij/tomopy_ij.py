import os
import glob
import sys
import shutil
from os.path import expanduser
from ij.gui import Line
from ij import IJ
from ij import ImagePlus
from ij.io import OpenDialog
from ij.plugin import ImageCalculator
from ij.plugin import FolderOpener
from java.awt.event import ActionListener, MouseAdapter
from javax.swing.event import ChangeEvent, ChangeListener
from javax.swing import JButton, JFrame, JPanel, JComboBox, JCheckBox, ButtonGroup, JOptionPane
from script.imglib import ImgLib
from java.awt import event, Font
from ch.psi.imagej.hdf5 import HDF5Reader, HDF5Utilities
from hdf.object.h5 import H5File
from hdf.object import Dataset

# Linux/MacOS - replace username
# sys.path.append(('/Users/username/conda/tomopy-ij/tomopy_ij'))

# Windows - replace username
# sys.path.append('C:/Users/username/tomopy-ij/tomopy_ij')

#sys.path.append('/Users/decarlo/conda/tomopy-ij/tomopy_ij')
# sys.path.append('/local/fast/conda/tomopy-ij/tomopy_ij')
sys.path.append('/Users/decarlo/conda/tomopy-ij/tomopy_ij')

import panel
import fields
import utils
import config

def createContentPane():

    panel = JPanel()
    panel.setLayout(None)
    panel.setOpaque(1)
    return panel

def read_hdf_meta(file_name, hdf_path):
    
    dataFile = H5File(file_name, H5File.READ)
    fp = dataFile.get(hdf_path)

    if fp is not None:
        return fp.getData()[0]
    else:
        return 0

def read_hdf_theta(file_name, hdf_path):
    
    dataFile = H5File(file_name, H5File.READ)
    fp = dataFile.get(hdf_path)

    if fp is not None:
        return fp.getData()
    else:
        return 0

def datasetSelector(event):

    datasetChooser = OpenDialog("Select a dataset")
    file_name = datasetChooser.getFileName()
    folder = datasetChooser.getDirectory()
    full_file_name = str(folder) + str(file_name)
    flds.selectedDatasetField.setText(full_file_name)
    reco_parameters.FileLocation = full_file_name

    from ch.psi.imagej.hdf5 import HDF5Reader
    reader = HDF5Reader()
    stack = reader.open("",False, full_file_name, "/exchange/data", True)

    if file_name is None:
        print("User canceled the dialog!")
    else:
        dataset_parameters.set()
        dataset_parameters.fname = full_file_name
        dataset_parameters.energy = read_hdf_meta(full_file_name, "/measurement/instrument/monochromator/energy")
        dataset_parameters.propagation_distance = read_hdf_meta(full_file_name, "/measurement/instrument/camera_motor_stack/setup/camera_distance")
        dataset_parameters.pixel_size = read_hdf_meta(full_file_name, "/measurement/instrument/detection_system/objective/resolution")
        dataset_parameters.theta = read_hdf_theta(full_file_name, "/exchange/theta")
        dataset_parameters.thetaStart = round(dataset_parameters.theta[0], 3)
        dataset_parameters.thetaEnd = round(dataset_parameters.theta[-1], 3)
        dataset_parameters.height = stack.height
        dataset_parameters.width = stack.width
        flds.energyField.setText(str(dataset_parameters.energy))
        flds.propagation_distanceField.setText(str(dataset_parameters.propagation_distance))
        flds.pixel_sizeField.setText(str(dataset_parameters.pixel_size))
        flds.datasetThetaStartLabel.setText(str(dataset_parameters.thetaStart))
        flds.datasetThetaEndLabel.setText(str(dataset_parameters.thetaEnd))
        flds.datasetHLabel.setText(str(dataset_parameters.width))
        flds.datasetVLabel.setText(str(dataset_parameters.height))
        flds.centerField.setText(str(dataset_parameters.width/2))

        flds.datasetImageSizeLabel.setVisible(True)
        flds.datasetHLabel.setVisible(True)
        flds.datasetVLabel.setVisible(True)
        flds.datasetThetaLabel.setVisible(True)
        flds.datasetThetaStartLabel.setVisible(True)
        flds.datasetThetaEndLabel.setVisible(True)

def reconstruct(event):

    reco_parameters.readParametersFromGUI(dataset_parameters.originalRoiX)
    
    tomo_slice = flds.sliceField.getText()
    center = flds.centerField.getText()
    nsino_x_chunk = flds.nsino_x_chunkField.getText()
    center_search_width = flds.centerSearchField.getText()

    reco_parameters.algorithm = flds.algorithmChooser.getSelectedIndex()
    if reco_parameters.algorithm == 0:
        algorithm = "gridrec"

    energy = flds.energyField.getText()
    propagation_distance = flds.propagation_distanceField.getText()
    pixel_size = flds.pixel_sizeField.getText()
    alpha = flds.alphaField.getText()
    if flds.paganinBox.isSelected() == True:
        retrieve_phase_method = 'paganin'
    else:
        retrieve_phase_method = 'none'        

    reco_parameters.stripe_method = flds.stripe_methodChooser.getSelectedIndex()
    if reco_parameters.stripe_method == 0:
        stripe_method = "none"
    elif reco_parameters.stripe_method == 1:
        stripe_method = "fw"
    elif reco_parameters.stripe_method == 2:
        stripe_method = "ti"
    elif reco_parameters.stripe_method == 3:
        stripe_method = "sf"
    elif reco_parameters.stripe_method == 4:
        stripe_method = "vo-all"

    reco_parameters.filter = flds.filterChooser.getSelectedIndex()
    if reco_parameters.filter == 0:
        filter = "none"
    elif reco_parameters.filter == 1:
        filter = "shepp"
    elif reco_parameters.filter == 2:
        filter = "hann"
    elif reco_parameters.filter == 3:
        filter = "hamming"
    elif reco_parameters.filter == 4:
        filter = "ramlak"
    elif reco_parameters.filter == 5:
        filter = "parzen"
    elif reco_parameters.filter == 6:
        filter = "cosine"
    elif reco_parameters.filter == 7:
        filter = "butterworth"

    if int(tomo_slice) < 0:
        tomo_slice = 1
    elif int(tomo_slice) > dataset_parameters.height:
        tomo_slice = dataset_parameters.height - 1

    nsino = float(tomo_slice)/float(dataset_parameters.height)

    full_file_name = flds.selectedDatasetField.getText()
    head_tail = os.path.split(full_file_name)
    rec_folder = os.path.normpath(head_tail[0]) + "_rec"

    print("Reconstructing")
    if event.getSource() == oneSliceButton:
        print("Preview one slice")

        command = "tomopy recon --file-name " + full_file_name + " --retrieve-phase-method " + retrieve_phase_method + " --energy " + str(energy) + " --propagation-distance " + str(propagation_distance) + " --pixel-size " + str(pixel_size) + " --retrieve-phase-alpha " + str(alpha) + " --rotation-axis " + center + " --rotation-axis-auto manual " + "--reconstruction-algorithm " + algorithm + " --gridrec-filter " + filter + " --reconstruction-type slice " + "--nsino " + str(nsino) + " --gridrec-padding " + " --remove-stripe-method " + stripe_method + " --fw-pad "
        print(command)
        os.system(command)

 
        list_of_files = glob.glob(os.path.join(rec_folder, "slice_rec", "*"))
        latest_file = max(list_of_files, key = os.path.getctime)
        imageResult = IJ.openImage(latest_file)
        imageResult.show()

    elif event.getSource() == tryButton:

        print("Try center")
        rec_file_name = head_tail[1].rstrip(".h5")
        try_folder = os.path.join(rec_folder, "try_center", rec_file_name)
        if os.path.isdir(try_folder) == True:
            shutil.rmtree(try_folder)

        command = "tomopy recon --file-name " + full_file_name + " --retrieve-phase-method " + retrieve_phase_method + " --energy " + str(energy) + " --propagation-distance " + str(propagation_distance) + " --pixel-size " + str(pixel_size) + " --retrieve-phase-alpha " + str(alpha) + " --rotation-axis " + center + " --rotation-axis-auto manual " + "--reconstruction-algorithm " + algorithm + " --gridrec-filter " + filter + " --reconstruction-type try " + "--center-search-width " + str(center_search_width) + " --nsino " + str(nsino) + " --gridrec-padding " + " --remove-stripe-method " + stripe_method + " --fw-pad "
        print(command)
        os.system(command)
        imp = FolderOpener.open(try_folder, "virtual")
        imp.show()

    elif event.getSource() == fullButton:

        print("Full")

        rec_folder = head_tail[1].rstrip(".h5") + "_rec"
        if os.path.isdir(rec_folder) == True:
            shutil.rmtree(rec_folder)

        command = "tomopy recon --file-name " + full_file_name + " --retrieve-phase-method " + retrieve_phase_method + " --energy " + str(energy) + " --propagation-distance " + str(propagation_distance) + " --pixel-size " + str(pixel_size) + " --retrieve-phase-alpha " + str(alpha) + " --rotation-axis " + center + " --rotation-axis-auto manual " + "--reconstruction-algorithm " + algorithm + " --gridrec-filter " + filter + " --reconstruction-type full " + " --gridrec-padding " + " --nsino-per-chunk " + nsino_x_chunk
        print(command)
        os.system(command)
        
        imp = FolderOpener.open(rec_folder, "virtual")
        imp.show()

    reco_parameters.writeParametersToFile()


# To have the same look on all platforms
JFrame.setDefaultLookAndFeelDecorated(1)
frame = JFrame("Reconstruction User Interface")

contentPane = createContentPane()
frame.setContentPane(contentPane)

GUI = panel.Panel()
flds = fields.Fields(GUI)

dataset_parameters = config.DatasetParameters(flds)
reco_parameters = config.RecoParameters(flds)

# Create a panel for choosing a dataset
contentPane.add(flds.chooseDatasetPanel)
flds.chooseDatasetPanel.add(flds.datasetSelectionLabel)
flds.chooseDatasetPanel.add(flds.selectedDatasetField)
flds.chooseDatasetPanel.add(flds.datasetImageSizeLabel)
flds.chooseDatasetPanel.add(flds.datasetHLabel)
flds.chooseDatasetPanel.add(flds.datasetVLabel)

flds.chooseDatasetPanel.add(flds.datasetThetaLabel)
flds.chooseDatasetPanel.add(flds.datasetThetaStartLabel)
flds.chooseDatasetPanel.add(flds.datasetThetaEndLabel)

flds.chooseDatasetPanel.add(flds.datasetSelectionButton)
flds.datasetSelectionButton.actionPerformed = datasetSelector

# Expert box
flds.chooseDatasetPanel.add(flds.expertBox)

# 360t box
flds.chooseDatasetPanel.add(flds.flipStichBox)

# Create a panel for reconstrution settings
contentPane.add(flds.recoSettingsPanel)
flds.recoSettingsPanel.add(flds.recoSettingsLabel)

# Create a panel for reconstrution settings
contentPane.add(flds.recoSettingsPanel)
flds.recoSettingsPanel.add(flds.recoSettingsLabel)

# Algorithm selection
flds.recoSettingsPanel.add(flds.algorithmLabel)
flds.recoSettingsPanel.add(flds.algorithmChooser)

# Paganin
flds.recoSettingsPanel.add(flds.energyLabel)
flds.recoSettingsPanel.add(flds.energyField)
flds.recoSettingsPanel.add(flds.energyUnitsLabel)
flds.recoSettingsPanel.add(flds.propagation_distanceLabel)
flds.recoSettingsPanel.add(flds.propagation_distanceField)
flds.recoSettingsPanel.add(flds.propagation_distanceUnitsLabel)
flds.recoSettingsPanel.add(flds.pixel_sizeLabel)
flds.recoSettingsPanel.add(flds.pixel_sizeField)
flds.recoSettingsPanel.add(flds.pixel_sizeUnitsLabel)
flds.recoSettingsPanel.add(flds.alphaLabel)
flds.recoSettingsPanel.add(flds.alphaField)

# Paganin box
flds.recoSettingsPanel.add(flds.paganinBox)

# filter
flds.recoSettingsPanel.add(flds.filterLabel)
flds.recoSettingsPanel.add(flds.filterChooser)

# Rotation center
flds.recoSettingsPanel.add(flds.centerLabel)
flds.recoSettingsPanel.add(flds.centerField)

# Remove Stripe Method
flds.recoSettingsPanel.add(flds.stripe_methodLabel)
flds.recoSettingsPanel.add(flds.stripe_methodChooser)

# Slice number
flds.recoSettingsPanel.add(flds.sliceLabel)
flds.recoSettingsPanel.add(flds.sliceField)

# Center Search Width
flds.recoSettingsPanel.add(flds.centerSearchLabel)
flds.recoSettingsPanel.add(flds.centerSearchField)
flds.recoSettingsPanel.add(flds.centerSearchUnitsLabel)

# nsino_x_chunk
flds.recoSettingsPanel.add(flds.nsino_x_chunkLabel)
flds.recoSettingsPanel.add(flds.nsino_x_chunkField)

# Queue selection
flds.recoSettingsPanel.add(flds.queueLabel)
flds.recoSettingsPanel.add(flds.localButton)
flds.recoSettingsPanel.add(flds.alcfButton)
flds.recoSettingsPanel.add(flds.lcrcButton)
queueGroup = ButtonGroup()
queueGroup.add(flds.localButton)
queueGroup.add(flds.lcrcButton)
queueGroup.add(flds.alcfButton)

# Number of nodes
flds.recoSettingsPanel.add(flds.nnodeLabel)
flds.recoSettingsPanel.add(flds.nnodeChooser)

# One slice reconstruction
oneSliceButton = GUI.createButton("Preview one slice",10, 275, 200, 40, 12, True)
oneSliceButton.actionPerformed = reconstruct
flds.recoSettingsPanel.add(oneSliceButton)

# Try Reconstruction
tryButton = GUI.createButton("Try Reconstruction",10, 325, 200, 40, 12, True)
tryButton.actionPerformed = reconstruct
flds.recoSettingsPanel.add(tryButton)

# Submit to the cluster
fullButton = GUI.createButton("Full Reconstruction",10, 375, 200, 40, 12, True)
fullButton.actionPerformed = reconstruct
flds.recoSettingsPanel.add(fullButton)

frame.setSize(810, 830)      
frame.setVisible(1)

# Actions
algorithmParametersHandler = utils.AlgorithmParameters(flds.algorithmChooser, flds.filterChooser)
flds.algorithmChooser.actionListener = algorithmParametersHandler

expertSelectionHandler = utils.ExpertSelection(flds)
flds.expertBox.itemListener = expertSelectionHandler

paganinSelectionHandler = utils.PaganinSelection(flds)
flds.paganinBox.itemListener = paganinSelectionHandler

if os.path.exists(reco_parameters.pfname):
    print("Using previous parameter file")
else:
    print("Creating default parameter file %s", reco_parameters.pfname)       
    try:
        FILE = open(reco_parameters.pfname,"w+")
        FILE.write("FileName                   " + str(reco_parameters.fname) +"\n")
        FILE.write("Algorithm                  " + str(reco_parameters.algorithm) +"\n")
        FILE.write("Filter                     " + str(reco_parameters.filter_index) +"\n")
        FILE.write("RemoveStripeMethod         " + str(reco_parameters.stripe_method) +"\n")
        FILE.write("Center                     " + str(reco_parameters.center) +"\n")
        FILE.write("Slice                      " + str(reco_parameters.slice) +"\n")
        FILE.write("NsinoPerChunk              " + str(reco_parameters.nsino_x_chunk) +"\n")
        FILE.write("SearchWidth                " + str(reco_parameters.center_search_width) +"\n")
        FILE.write("Energy                     " + str(reco_parameters.energy) +"\n")
        FILE.write("PropagationDistance        " + str(reco_parameters.propagation_distance) +"\n")
        FILE.write("PixelSize                  " + str(reco_parameters.pixel_size) +"\n")
        FILE.write("Alpha                      " + str(reco_parameters.alpha) +"\n")
        FILE.write("Queue                      " + str(reco_parameters.queue) +"\n")
        FILE.write("Nnodes                     " + str(reco_parameters.nnodes) +"\n")
        FILE.write("\n")
        FILE.close()
    except IOError:
        pass

reco_parameters.readParametersFromFile()
reco_parameters.writeParametersToGUI()