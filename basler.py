import time
from pypylon import pylon
import cv2
import sys
import json
import os
from utility import ePrint

class CameraEventHandler(pylon.ConfigurationEventHandler):
    def __init__(self, basler):
        self.basler = basler
        super().__init__()
        ePrint("CameraEventHandler init")

    def OnAttach(self, camera):
        ePrint(f'Before attaching the camera {camera}')

    def OnAttached(self, camera):
        ePrint(f'Attached: {camera.GetDeviceInfo()}')

    def OnOpen(self, camera):
        ePrint('Before opening...')

    def OnOpened(self, camera):
        ePrint('After Opening')
        ePrint(self.basler.config)
        self.basler.defaultSettingsFromConfig()

    def OnDestroy(self, camera):
        ePrint('Before destroying')

    def OnDestroyed(self, camera):
        ePrint('After destroying')

    def OnClosed(self, camera):
        ePrint('Camera Closed')

    def OnDetach(self, camera):
        ePrint('Detaching')

    def OnGrabStarted(self, camera):
        ePrint('Grab started')


# Image Event Handler
class ImageEventHandler(pylon.ImageEventHandler):
    def __init__(self, basler):
        self.basler = basler
        super().__init__()
        ePrint("ImageDataHandler init")

    def OnImagesSkipped(self, camera, countOfSkippedImages):
        ePrint("OnImagesSkipped event for device ", camera.GetDeviceInfo().GetModelName())
        ePrint(countOfSkippedImages, " images have been skipped.")


    def OnImageGrabbed(self, camera, grabResult):
        try:
            if grabResult.GrabSucceeded():
                start = time.perf_counter()
                converted_image = self.basler.converter.Convert(grabResult)
                grabResult.Release()
                image_array = converted_image.GetArray()

                if self.basler.resize:
                    width = self.basler.resize_width
                    height = self.basler.resize_height
                    image_array = cv2.resize(image_array, dsize=(width, height), interpolation=cv2.INTER_CUBIC)

                if self.basler.crop:
                    startY = self.basler.crop_startY
                    endY = self.basler.crop_endY
                    startX = self.basler.crop_startX
                    endX = self.basler.crop_endX
                    image_array = image_array[startY:endY, startX:endX]

                encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), self.basler.image_quality]
                jpeg = cv2.imencode(".JPEG", image_array, encode_param)[1]
                self.basler.frame_buffer.write(jpeg)
                ePrint("Image grab: %.3f ms" % (time.perf_counter()-start))
            else:
                ePrint("Error: ", grabResult.ErrorCode, grabResult.ErrorDescription)
            grabResult.Release()
        except Exception as e:
            ePrint(e)


class Basler:
    def __init__(self, config, camera_id, frame_buffer):
        self.settings = {}
        # The name of the pylon file handle
        script_path = os.path.dirname(os.path.realpath(__file__))

        self.nodeFile = script_path+'/'+'configurations'+'/'+camera_id+".pfs"
        self.config = config
        self.camera = {}
        self.converter = {}
        self.frame_buffer = frame_buffer

        self.image_quality = config["converter"]["ImageQuality"]

        self.resize = config["converter"]["Resize"]["enable"]
        self.resize_width = config["converter"]["Resize"]["width"]
        self.resize_height = config["converter"]["Resize"]["height"]

        self.crop = config["converter"]["Crop"]["enable"]
        self.crop_startY = config["converter"]["Crop"]["startY"]
        self.crop_endY = config["converter"]["Crop"]["endY"]
        self.crop_startX = config["converter"]["Crop"]["startX"]
        self.crop_endX = config["converter"]["Crop"]["endX"]

        self.stop = False
        self.openCamera(camera_id)
        self.configureImageConverter()
        self.configureAndStartGrabLoop()


    def defaultSettingsFromConfig(self):
        '''
        self.camera.BalanceWhiteAuto.SetValue("Off")
        #self.camera.BinningHorizontal.SetValue(1)
        #self.camera.BinningVertical.SetValue(1)
        '''

    def openCamera(self, cameraID):
        info = pylon.DeviceInfo()
        info.SetSerialNumber(cameraID)

        self.camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice(info))
        self.camera.MaxNumBuffer = 30
        self.camera.RegisterConfiguration(CameraEventHandler(self), pylon.RegistrationMode_Append, pylon.Cleanup_Delete)
        self.camera.RegisterImageEventHandler(ImageEventHandler(self), pylon.RegistrationMode_Append,
                                              pylon.Cleanup_Delete)

        ePrint("Using device: ", self.camera.GetDeviceInfo().GetModelName())
        self.camera.Open()

        # ePrint("Saving camera's node map to file...")
        # Save the content of the camera's node map into the file.
        # pylon.FeaturePersistence.Save(self.nodeFile, self.camera.GetNodeMap())

        ePrint("Reading configuration file: %s "+self.nodeFile)
        pylon.FeaturePersistence.Load(self.nodeFile, self.camera.GetNodeMap(), True)

        ePrint(self.camera.GetNodeMap())
        time.sleep(1)

    def configureImageConverter(self):
        self.converter = pylon.ImageFormatConverter()
        self.converter.OutputOrientation = self.config["converter"]["Orientation"]
        #self.converter.OutputPixelFormat = pylon.PixelType_BayerBG8
        self.converter.OutputPixelFormat = pylon.PixelType_BGR8packed
        self.converter.OutputBitAlignment = pylon.OutputBitAlignment_MsbAligned

    def configureAndStartGrabLoop(self):
        if self.config["converter"]["GrabStrategy"] == "OneByOne":
            ePrint("GrabStrategy: %s" % "OneByOne")
            self.camera.StartGrabbing(pylon.GrabStrategy_OneByOne, pylon.GrabLoop_ProvidedByInstantCamera)
        elif self.config["converter"]["GrabStrategy"] == "LatestImageOnly":
            ePrint("GrabStrategy: %s" % "LatestImageOnly")
            self.camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly, pylon.GrabLoop_ProvidedByInstantCamera)
        else:
            ePrint("GrabStrategy: Not configured... Using LatestImageOnly.")
            self.camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly, pylon.GrabLoop_ProvidedByInstantCamera)

    def stopGrabbingImages(self):
        self.stop = True
        self.camera.StopGrabbing()
        self.camera.Close()

    def cameraCommandHandler(self):
        while not self.stop:
            try:
                for line in sys.stdin:
                    try:
                        commands = json.loads(line.rstrip())
                        ePrint("received commands", commands)

                        for command in commands:
                            for key in command:

                                if key == "BalanceWhiteAuto":
                                    # print("Execute BalanceWhiteAuto")
                                    self.camera.BalanceWhiteAuto.SetValue(command[key])
                                elif key == "Height":
                                    self.camera.Height.SetValue(command[key])
                                elif key == "Width":
                                    self.camera.Width.SetValue(command[key])
                                elif key == "BinningHorizontal":
                                    self.camera.BinningHorizontal.SetValue(command[key])
                                elif key == "BinningVertical":
                                    self.camera.BinningVertical.SetValue(command[key])
                                elif key == "CenterY":
                                    self.camera.CenterY.SetValue(command[key])
                                elif key == "ReverseX":
                                    self.camera.ReverseX.SetValue(command[key])
                                elif key == "ExposureAuto":
                                    self.camera.ExposureAuto.SetValue(command[key])
                                elif key == "GainAuto":
                                    self.camera.GainAuto.SetValue(command[key])
                                elif key == "BlackLevelRaw":
                                    self.camera.BlackLevelRaw.SetValue(command[key])
                                elif key == "GammaEnable":
                                    self.camera.GammaEnable.SetValue(command[key])
                                elif key == "GammaSelector":
                                    self.camera.GammaSelector.SetValue(command[key])
                                elif key == "PixelFormat":
                                    self.camera.PixelFormat.SetValue(command[key])
                                elif key == "ProcessedRawEnable":
                                    self.camera.ProcessedRawEnable.SetValue(command[key])
                                elif key == "LightSourceSelector":
                                    self.camera.LightSourceSelector.SetValue(command[key])
                                elif key == "AcquisitionFrameRateEnable":
                                    self.camera.AcquisitionFrameRateEnable.SetValue(command[key])
                                elif key == "AcquisitionFrameRateAbs":
                                    self.camera.AcquisitionFrameRateAbs.SetValue(command[key])
                                elif key == "AutoTargetValue":
                                    self.camera.AutoTargetValue.SetValue(command[key])
                                elif key == "AutoGainRawLowerLimit":
                                    self.camera.AutoGainRawLowerLimit.SetValue(command[key])
                                elif key == "AutoGainRawUpperLimit":
                                    self.camera.AutoGainRawUpperLimit.SetValue(command[key])
                                elif key == "AutoExposureTimeAbsLowerLimit":
                                    self.camera.AutoExposureTimeAbsLowerLimit.SetValue(command[key])
                                elif key == "AutoExposureTimeAbsUpperLimit":
                                    self.camera.AutoExposureTimeAbsUpperLimit.SetValue(command[key])
                                elif key == "AutoFunctionProfile":
                                    self.camera.AutoFunctionProfile.SetValue(command[key])
                                elif key == "AutoFunctionAOIWidth":
                                    self.camera.AutoFunctionAOIWidth.SetValue(command[key])
                                elif key == "AutoFunctionAOIHeight":
                                    self.camera.AutoFunctionAOIHeight.SetValue(command[key])
                                elif key == "AutoFunctionAOIOffsetX":
                                    self.camera.AutoFunctionAOIOffsetX.SetValue(command[key])
                                elif key == "AutoFunctionAOIOffsetY":
                                    self.camera.AutoFunctionAOIOffsetY.SetValue(command[key])
                                elif key == "AutoFunctionAOIUsageIntensity":
                                    self.camera.AutoFunctionAOIUsageIntensity.SetValue(command[key])
                                elif key == "AutoFunctionAOIUsageWhiteBalance":
                                    self.camera.AutoFunctionAOIUsageWhiteBalance.SetValue(command[key])
                                elif key == "SetDefault":
                                    self.defaultSettingsFromConfig()
                                elif key == "PrintSettings":
                                    ePrint(self.settings)
                                else:
                                    ePrint("Command not implemented")
                    except Exception as e:
                        ePrint("Command is not valid JSON:", e)

            except Exception as e:
                ePrint(e)
            finally:
                time.sleep(1)
