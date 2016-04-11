import os
import unittest
import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
import logging

#
# ScreenCapture
#

class ScreenCapture(ScriptedLoadableModule):
  """Uses ScriptedLoadableModule base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "Screen Capture"
    self.parent.categories = ["Utilities"]
    self.parent.dependencies = []
    self.parent.contributors = ["Andras Lasso (PerkLab, Queen's)"]
    self.parent.helpText = """Capture image sequences from 2D and 3D viewers"""
    self.parent.acknowledgementText = """ """ # replace with organization, grant and thanks.

#
# ScreenCaptureWidget
#

class ScreenCaptureWidget(ScriptedLoadableModuleWidget):
  """Uses ScriptedLoadableModuleWidget base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def setup(self):
    ScriptedLoadableModuleWidget.setup(self)

    self.logic = ScreenCaptureLogic()
    self.logic.logCallback = self.addLog

    # Instantiate and connect widgets ...

    #
    # Parameters Area
    #
    sliceViewerSweepCollapsibleButton = ctk.ctkCollapsibleButton()
    sliceViewerSweepCollapsibleButton.text = "Slice viewer sweep"
    self.layout.addWidget(sliceViewerSweepCollapsibleButton)

    # Layout within the dummy collapsible button
    sliceViewerSweepFormLayout = qt.QFormLayout(sliceViewerSweepCollapsibleButton)

    # Input slice selector
    self.sliceViewSelector = slicer.qMRMLNodeComboBox()
    self.sliceViewSelector.nodeTypes = ["vtkMRMLSliceNode"]
    self.sliceViewSelector.addEnabled = False
    self.sliceViewSelector.removeEnabled = False
    self.sliceViewSelector.noneEnabled = False
    self.sliceViewSelector.showHidden = False
    self.sliceViewSelector.showChildNodeTypes = False
    self.sliceViewSelector.setMRMLScene( slicer.mrmlScene )
    self.sliceViewSelector.setToolTip( "Contents of this slice view will be captured." )
    sliceViewerSweepFormLayout.addRow("Slice view: ", self.sliceViewSelector)

    # Start slice offset position
    self.startSliceOffsetSliderWidget = ctk.ctkSliderWidget()
    self.startSliceOffsetSliderWidget.singleStep = 5
    self.startSliceOffsetSliderWidget.minimum = -100
    self.startSliceOffsetSliderWidget.maximum = 100
    self.startSliceOffsetSliderWidget.value = 0
    self.startSliceOffsetSliderWidget.setToolTip("Start slice offset.")
    sliceViewerSweepFormLayout.addRow("Start offset:", self.startSliceOffsetSliderWidget)

    # End slice offset position
    self.endSliceOffsetSliderWidget = ctk.ctkSliderWidget()
    self.endSliceOffsetSliderWidget.singleStep = 5
    self.endSliceOffsetSliderWidget.minimum = -100
    self.endSliceOffsetSliderWidget.maximum = 100
    self.endSliceOffsetSliderWidget.value = 0
    self.endSliceOffsetSliderWidget.setToolTip("End slice offset.")
    sliceViewerSweepFormLayout.addRow("End offset:", self.endSliceOffsetSliderWidget)
        
    # Number of steps value
    self.sliceSweepNumberOfStepsSliderWidget = ctk.ctkSliderWidget()
    self.sliceSweepNumberOfStepsSliderWidget.singleStep = 5
    self.sliceSweepNumberOfStepsSliderWidget.minimum = 2
    self.sliceSweepNumberOfStepsSliderWidget.maximum = 150
    self.sliceSweepNumberOfStepsSliderWidget.value = 30
    self.sliceSweepNumberOfStepsSliderWidget.decimals = 0
    self.sliceSweepNumberOfStepsSliderWidget.setToolTip("Number of images extracted between start and stop slice positions.")
    sliceViewerSweepFormLayout.addRow("Number of images:", self.sliceSweepNumberOfStepsSliderWidget)

    # Output directory selector
    self.outputDirSelector = ctk.ctkPathLineEdit()
    self.outputDirSelector.filters = ctk.ctkPathLineEdit.Dirs
    self.outputDirSelector.settingKey = 'ScreenCaptureOutputDir'
    sliceViewerSweepFormLayout.addRow("Output directory:", self.outputDirSelector)
    if not self.outputDirSelector.currentPath:
      defaultOutputPath = os.path.abspath(os.path.join(slicer.app.defaultScenePath,'Capture'))
      self.outputDirSelector.setCurrentPath(defaultOutputPath)

    self.fileNamePatternWidget = qt.QLineEdit()
    self.fileNamePatternWidget.setToolTip("String that defines file name, type, and numbering scheme. Default: image%05d.png.")
    self.fileNamePatternWidget.text = "image%05d.png"
    sliceViewerSweepFormLayout.addRow("File name pattern:", self.fileNamePatternWidget)
    
    # Capture button
    self.captureSliceSweep = qt.QPushButton("Capture")
    self.captureSliceSweep.toolTip = "Capture slice sweep to image sequence."
    sliceViewerSweepFormLayout.addRow(self.captureSliceSweep)
        
    self.statusLabel = qt.QPlainTextEdit()
    self.statusLabel.setTextInteractionFlags(qt.Qt.TextSelectableByMouse)
    self.statusLabel.setCenterOnScroll(True)
    sliceViewerSweepFormLayout.addRow(self.statusLabel)
    
    # Add vertical spacer
    self.layout.addStretch(1)
    
    # connections
    self.captureSliceSweep.connect('clicked(bool)', self.onCaptureSliceSweep)
    self.sliceViewSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.onSliceNodeSelected)
    self.startSliceOffsetSliderWidget.connect('valueChanged(double)', self.setSliceOffset)
    self.endSliceOffsetSliderWidget.connect('valueChanged(double)', self.setSliceOffset)

    self.onSliceNodeSelected()

  def addLog(self, text):
    """Append text to log window
    """
    self.statusLabel.appendPlainText(text)
    self.statusLabel.ensureCursorVisible()
    slicer.app.processEvents() # force update
    
  def cleanup(self):
    pass

  def onSliceNodeSelected(self):
    offsetResolution = self.logic.getSliceOffsetResolution(self.sliceViewSelector.currentNode())
    sliceOffsetMin, sliceOffsetMax = self.logic.getSliceOffsetRange(self.sliceViewSelector.currentNode())
    
    wasBlocked = self.startSliceOffsetSliderWidget.blockSignals(True)
    self.startSliceOffsetSliderWidget.singleStep = offsetResolution
    self.startSliceOffsetSliderWidget.minimum = sliceOffsetMin
    self.startSliceOffsetSliderWidget.maximum = sliceOffsetMax
    self.startSliceOffsetSliderWidget.value =  sliceOffsetMin
    self.startSliceOffsetSliderWidget.blockSignals(wasBlocked)
    
    wasBlocked = self.endSliceOffsetSliderWidget.blockSignals(True)
    self.endSliceOffsetSliderWidget.singleStep = offsetResolution
    self.endSliceOffsetSliderWidget.minimum =  sliceOffsetMin
    self.endSliceOffsetSliderWidget.maximum =  sliceOffsetMax
    self.endSliceOffsetSliderWidget.value =  sliceOffsetMax
    self.endSliceOffsetSliderWidget.blockSignals(wasBlocked)
    
  def setSliceOffset(self, offset):
    sliceLogic = self.logic.getSliceLogicFromSliceNode(self.sliceViewSelector.currentNode())
    sliceLogic.SetSliceOffset(offset) 
  
  def onSelect(self):
    self.captureSliceSweep.enabled = self.sliceViewSelector.currentNode()

  def onCaptureSliceSweep(self):
    slicer.app.setOverrideCursor(qt.Qt.WaitCursor)
    self.statusLabel.plainText = ''
    try:
      self.logic.captureSliceSweep(self.sliceViewSelector.currentNode(),
        self.startSliceOffsetSliderWidget.value, self.endSliceOffsetSliderWidget.value,
        int(self.sliceSweepNumberOfStepsSliderWidget.value),
        self.outputDirSelector.currentPath, self.fileNamePatternWidget.text)    
    except Exception as e:
      self.addLog("Unexpected error: {0}".format(e.message))
      import traceback
      traceback.print_exc()
    slicer.app.restoreOverrideCursor()

#
# ScreenCaptureLogic
#

class ScreenCaptureLogic(ScriptedLoadableModuleLogic):
  """This class should implement all the actual
  computation done by your module.  The interface
  should be such that other python code can import
  this class and make use of the functionality without
  requiring an instance of the Widget.
  Uses ScriptedLoadableModuleLogic base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def addLog(self, text):
    logging.info(text)
    if self.logCallback:
      self.logCallback(text)

  def getSliceLogicFromSliceNode(self, sliceNode):
    lm = slicer.app.layoutManager()
    sliceLogic = lm.sliceWidget(sliceNode.GetLayoutName()).sliceLogic()
    return sliceLogic
  
  def getSliceOffsetRange(self, sliceNode):
    sliceLogic = self.getSliceLogicFromSliceNode(sliceNode)
        
    sliceBounds = [0, -1, 0, -1, 0, -1]
    sliceLogic.GetLowestVolumeSliceBounds(sliceBounds);
    sliceOffsetMin = sliceBounds[4]
    sliceOffsetMax = sliceBounds[5]

    # increase range if it is empty
    # to allow capturing even when no volumes are shown in slice views
    if sliceOffsetMin == sliceOffsetMax:
      sliceOffsetMin = sliceLogic.GetSliceOffset()-100
      sliceOffsetMax = sliceLogic.GetSliceOffset()+100
      
    return sliceOffsetMin, sliceOffsetMax
    
  def getSliceOffsetResolution(self, sliceNode):
    sliceLogic = self.getSliceLogicFromSliceNode(sliceNode)
    
    sliceOffsetResolution = 1.0
    sliceSpacing = sliceLogic.GetLowestVolumeSliceSpacing();
    if sliceSpacing is not None and sliceSpacing[2]>0:
      sliceOffsetResolution = sliceSpacing[2]

    return sliceOffsetResolution
      
  def captureSliceSweep(self, sliceNode, startSliceOffset, endSliceOffset, numberOfImages, outputDir, outputFilenamePattern):
    sliceLogic = self.getSliceLogicFromSliceNode(sliceNode)

    if not os.path.exists(outputDir):
      os.makedirs(outputDir)

    filePathPattern = os.path.join(outputDir,outputFilenamePattern)

    sliceView = slicer.app.layoutManager().sliceWidget(sliceNode.GetLayoutName()).sliceView()
    compositeNode = sliceLogic.GetSliceCompositeNode()
    offsetStepSize = (endSliceOffset-startSliceOffset)/(numberOfImages-1)
    for offsetIndex in range(numberOfImages):
      sliceLogic.SetSliceOffset(startSliceOffset+offsetIndex*offsetStepSize)
      sliceView.forceRender()
      pixmap = qt.QPixmap().grabWidget(sliceView)
      filename = filePathPattern % offsetIndex
      self.addLog("Write "+filename)
      pixmap.save(filename)
      offsetIndex += 1
    self.addLog("Done.")
      
  def takeScreenshot(self,name,description,type=-1):
    # show the message even if not taking a screen shot
    slicer.util.delayDisplay('Take screenshot: '+description+'.\nResult is available in the Annotations module.', 3000)

    lm = slicer.app.layoutManager()
    # switch on the type to get the requested window
    widget = 0
    if type == slicer.qMRMLScreenShotDialog.FullLayout:
      # full layout
      widget = lm.viewport()
    elif type == slicer.qMRMLScreenShotDialog.ThreeD:
      # just the 3D window
      widget = lm.threeDWidget(0).threeDView()
    elif type == slicer.qMRMLScreenShotDialog.Red:
      # red slice window
      widget = lm.sliceWidget("Red")
    elif type == slicer.qMRMLScreenShotDialog.Yellow:
      # yellow slice window
      widget = lm.sliceWidget("Yellow")
    elif type == slicer.qMRMLScreenShotDialog.Green:
      # green slice window
      widget = lm.sliceWidget("Green")
    else:
      # default to using the full window
      widget = slicer.util.mainWindow()
      # reset the type so that the node is set correctly
      type = slicer.qMRMLScreenShotDialog.FullLayout

    # grab and convert to vtk image data
    qpixMap = qt.QPixmap().grabWidget(widget)
    qimage = qpixMap.toImage()
    imageData = vtk.vtkImageData()
    slicer.qMRMLUtils().qImageToVtkImageData(qimage,imageData)

    annotationLogic = slicer.modules.annotations.logic()
    annotationLogic.CreateSnapShot(name, description, type, 1, imageData)

class ScreenCaptureTest(ScriptedLoadableModuleTest):
  """
  This is the test case for your scripted module.
  Uses ScriptedLoadableModuleTest base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def setUp(self):
    """ Do whatever is needed to reset the state - typically a scene clear will be enough.
    """
    slicer.mrmlScene.Clear(0)

  def runTest(self):
    """Run as few or as many tests as needed here.
    """
    self.setUp()
    self.test_ScreenCapture1()

  def test_ScreenCapture1(self):
    """ Ideally you should have several levels of tests.  At the lowest level
    tests should exercise the functionality of the logic with different inputs
    (both valid and invalid).  At higher levels your tests should emulate the
    way the user would interact with your code and confirm that it still works
    the way you intended.
    One of the most important features of the tests is that it should alert other
    developers when their changes will have an impact on the behavior of your
    module.  For example, if a developer removes a feature that you depend on,
    your test should break so they know that the feature is needed.
    """

    self.delayDisplay("Starting the test")
    #
    # first, get some data
    #
    import urllib
    downloads = (
        ('http://slicer.kitware.com/midas3/download?items=5767', 'FA.nrrd', slicer.util.loadVolume),
        )

    for url,name,loader in downloads:
      filePath = slicer.app.temporaryPath + '/' + name
      if not os.path.exists(filePath) or os.stat(filePath).st_size == 0:
        logging.info('Requesting download %s from %s...\n' % (name, url))
        urllib.urlretrieve(url, filePath)
      if loader:
        logging.info('Loading %s...' % (name,))
        loader(filePath)
    self.delayDisplay('Finished with download and loading')

    volumeNode = slicer.util.getNode(pattern="FA")
    logic = ScreenCaptureLogic()
    self.assertIsNotNone( logic.hasImageData(volumeNode) )
    self.delayDisplay('Test passed!')
