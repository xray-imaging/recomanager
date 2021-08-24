import os, shutil
from java.awt.event import ActionListener, ItemListener
from java.awt import event
from javax.swing import JOptionPane
from ij import IJ


class AlgorithmParameters(event.ActionListener):

    def __init__(self, algoC, filterC):

        self.algoC = algoC
        self.filterC = filterC
        
    def actionPerformed(self, event):
    
        algorithmOption = self.algoC.getSelectedIndex()
        if algorithmOption == 0:
            self.filterC.setSelectedIndex(5)
        elif algorithmOption == 1:
            self.filterC.setSelectedIndex(4)
        elif algorithmOption == 2:
            IJ.showMessage("This option has not been implemented yet!" )            
            self.algoC.setSelectedIndex(0)
            self.filterC.setSelectedIndex(5)

class PaganinSelection(event.ItemListener):

    def __init__(self, fields):

        self.fields = fields

    def itemStateChanged(self, event):

        if self.fields.paganinBox.isSelected() == True:
            self.fields.energyLabel.setVisible(True)
            self.fields.energyField.setVisible(True)
            self.fields.energyUnitsLabel.setVisible(True)
            self.fields.propagation_distanceLabel.setVisible(True)
            self.fields.propagation_distanceField.setVisible(True)
            self.fields.propagation_distanceUnitsLabel.setVisible(True)
            self.fields.pixel_sizeLabel.setVisible(True)
            self.fields.pixel_sizeField.setVisible(True)
            self.fields.pixel_sizeUnitsLabel.setVisible(True)
            self.fields.alphaLabel.setVisible(True)
            self.fields.alphaField.setVisible(True)

        else:
            self.fields.energyLabel.setVisible(False)
            self.fields.energyField.setVisible(False)
            self.fields.energyUnitsLabel.setVisible(False)
            self.fields.propagation_distanceLabel.setVisible(False)
            self.fields.propagation_distanceField.setVisible(False)
            self.fields.propagation_distanceUnitsLabel.setVisible(False)
            self.fields.pixel_sizeLabel.setVisible(False)
            self.fields.pixel_sizeField.setVisible(False)
            self.fields.pixel_sizeUnitsLabel.setVisible(False)
            self.fields.alphaLabel.setVisible(False)
            self.fields.alphaField.setVisible(False)

class ExpertSelection(event.ItemListener):

    def __init__(self, fields):

        self.fields = fields

    def itemStateChanged(self, event):

        if self.fields.expertBox.isSelected() == True:

            self.fields.sliceLabel.setVisible(True)
            self.fields.sliceField.setVisible(True)
            self.fields.nsino_x_chunkLabel.setVisible(True)
            self.fields.nsino_x_chunkField.setVisible(True)
            self.fields.centerSearchLabel.setVisible(True)
            self.fields.centerSearchField.setVisible(True)
            self.fields.centerSearchUnitsLabel.setVisible(True)
            self.fields.queueLabel.setVisible(True)
            self.fields.localButton.setVisible(True)
            self.fields.lcrcButton.setVisible(True)
            self.fields.alcfButton.setVisible(True)
            self.fields.nnodeLabel.setVisible(True)
            self.fields.nnodeChooser.setVisible(True)
        else:
            self.fields.sliceLabel.setVisible(False)
            self.fields.sliceField.setVisible(False)
            self.fields.nsino_x_chunkLabel.setVisible(False)
            self.fields.nsino_x_chunkField.setVisible(False)
            self.fields.centerSearchLabel.setVisible(False)
            self.fields.centerSearchField.setVisible(False)
            self.fields.centerSearchUnitsLabel.setVisible(False)
            self.fields.queueLabel.setVisible(False)
            self.fields.localButton.setVisible(False)
            self.fields.lcrcButton.setVisible(False)
            self.fields.alcfButton.setVisible(False)
            self.fields.nnodeLabel.setVisible(False)
            self.fields.nnodeChooser.setVisible(False)
