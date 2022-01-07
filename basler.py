import time
from pypylon import pylon
import cv2
import sys
import json
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
                converted_image = self.basler.converter.Convert(grabResult)
                grabResult.Release()
                image_array = converted_image.GetArray()
                encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), self.basler.image_quality]
                jpeg = cv2.imencode(".JPEG", image_array, encode_param)[1].tostring()
                self.basler.frame_buffer.write(jpeg)
            else:
                ePrint("Error: ", grabResult.ErrorCode, grabResult.ErrorDescription)
            grabResult.Release()
        except Exception as e:
            ePrint(e)


class Basler:
    def __init__(self, config, camera_id, frame_buffer):
        self.settings = {}
        self.config = config
        self.camera = {}
        self.converter = {}
        self.frame_buffer = frame_buffer
        self.image_quality = config["converter"]["ImageQuality"]
        self.stop = False

        self.openCamera(camera_id)
        self.configureImageConverter()
        self.configureAndStartGrabLoop()

    def defaultSettingsFromConfig(self):
        # configure camera
        # Set initial values for some specific parameters
        self.camera.BalanceWhiteAuto.SetValue("Off")
        self.camera.BinningHorizontal.SetValue(1)
        self.camera.BinningVertical.SetValue(1)
        self.camera.Height.SetValue(self.config["camera"]["Height"])
        self.camera.Width.SetValue(self.config["camera"]["Width"])
        self.camera.BinningHorizontal.SetValue(self.config["camera"]["BinningHorizontal"])
        self.camera.BinningVertical.SetValue(self.config["camera"]["BinningVertical"])
        self.camera.Height.SetValue(self.config["camera"]["Height"])
        self.camera.CenterY.SetValue(self.config["camera"]["CenterY"])
        self.camera.ReverseX.SetValue(self.config["camera"]["ReverseX"])
        self.camera.ExposureAuto.SetValue(self.config["camera"]["ExposureAuto"])
        self.camera.GainAuto.SetValue(self.config["camera"]["GainAuto"])
        self.camera.BlackLevelRaw.SetValue(self.config["camera"]["BlackLevelRaw"])
        self.camera.GammaEnable.SetValue(self.config["camera"]["GammaEnable"])
        self.camera.GammaSelector.SetValue(self.config["camera"]["GammaSelector"])
        self.camera.PixelFormat.SetValue(self.config["camera"]["PixelFormat"])
        self.camera.ProcessedRawEnable.SetValue(self.config["camera"]["ProcessedRawEnable"])
        self.camera.LightSourceSelector.SetValue(self.config["camera"]["LightSourceSelector"])
        self.camera.AcquisitionFrameRateEnable.SetValue(self.config["camera"]["AcquisitionFrameRateEnable"])
        self.camera.AcquisitionFrameRateAbs.SetValue(self.config["camera"]["AcquisitionFrameRateAbs"])
        self.camera.AutoTargetValue.SetValue(self.config["camera"]["AutoTargetValue"])
        self.camera.AutoGainRawLowerLimit.SetValue(self.config["camera"]["AutoGainRawLowerLimit"])
        self.camera.AutoGainRawUpperLimit.SetValue(self.config["camera"]["AutoGainRawUpperLimit"])
        self.camera.AutoExposureTimeAbsLowerLimit.SetValue(self.config["camera"]["AutoExposureTimeAbsLowerLimit"])
        self.camera.AutoExposureTimeAbsUpperLimit.SetValue(self.config["camera"]["AutoExposureTimeAbsUpperLimit"])
        self.camera.AutoFunctionProfile.SetValue(self.config["camera"]["AutoFunctionProfile"])
        self.camera.AutoFunctionAOIWidth.SetValue(self.config["camera"]["AutoFunctionAOIWidth"])
        self.camera.AutoFunctionAOIHeight.SetValue(self.config["camera"]["AutoFunctionAOIHeight"])
        self.camera.AutoFunctionAOIOffsetX.SetValue(self.config["camera"]["AutoFunctionAOIOffsetX"])
        self.camera.AutoFunctionAOIOffsetY.SetValue(self.config["camera"]["AutoFunctionAOIOffsetY"])
        self.camera.AutoFunctionAOIUsageIntensity.SetValue(self.config["camera"]["AutoFunctionAOIUsageIntensity"])
        self.camera.AutoFunctionAOIUsageWhiteBalance.SetValue(self.config["camera"]["AutoFunctionAOIUsageWhiteBalance"])
        self.camera.BalanceWhiteAuto.SetValue(self.config["camera"]["BalanceWhiteAuto"])

    def openCamera(self, cameraID):
        info = pylon.DeviceInfo()
        info.SetSerialNumber(cameraID)
        self.camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice(info))
        self.camera.RegisterConfiguration(CameraEventHandler(self), pylon.RegistrationMode_Append, pylon.Cleanup_Delete)
        self.camera.RegisterImageEventHandler(ImageEventHandler(self), pylon.RegistrationMode_Append,
                                              pylon.Cleanup_Delete)
        self.camera.Open()

        # Read back current camera settings
        self.settings["deviceID"] = self.camera.DeviceID.GetValue()
        self.settings["DeviceModelName"] = self.camera.DeviceModelName.GetValue()
        self.settings["DeviceVersion"] = self.camera.DeviceVersion.GetValue()
        self.settings["DeviceFirmwareVersion"] = self.camera.DeviceFirmwareVersion.GetValue()
        self.settings["Vendor Name"] = self.camera.DeviceVendorName.GetValue()

        self.settings["Width"] = self.camera.Width.GetValue()
        self.settings["Height"] = self.camera.Height.GetValue()
        self.settings["CenterY"] = self.camera.CenterY.GetValue()
        self.settings["ReverseX"] = self.camera.ReverseX.GetValue()
        self.settings["BinningHorizontal"] = self.camera.BinningHorizontal.GetValue()
        self.settings["BinningVertical"] = self.camera.BinningVertical.GetValue()

        self.settings["ExposureAuto"] = self.camera.ExposureAuto.GetValue()
        self.settings["GainAuto"] = self.camera.GainAuto.GetValue()

        self.settings["BlackLevelRaw"] = self.camera.BlackLevelRaw.GetValue()
        self.settings["GammaEnable"] = self.camera.GammaEnable.GetValue()
        self.settings["GammaSelector"] = self.camera.GammaSelector.GetValue()
        self.settings["PixelFormat"] = self.camera.PixelFormat.GetValue()
        self.settings["ProcessedRawEnable"] = self.camera.ProcessedRawEnable.GetValue()
        self.settings["BalanceWhiteAuto"] = self.camera.BalanceWhiteAuto.GetValue()
        self.settings["LightSourceSelector"] = self.camera.LightSourceSelector.GetValue()
        self.settings["AcquisitionFrameRateEnable"] = self.camera.AcquisitionFrameRateEnable.GetValue()
        self.settings["AcquisitionFrameRateAbs"] = self.camera.AcquisitionFrameRateAbs.GetValue()

        self.settings["AutoTargetValue"] = self.camera.AutoTargetValue.GetValue()
        self.settings["AutoGainRawLowerLimit"] = self.camera.AutoGainRawLowerLimit.GetValue()
        self.settings["AutoGainRawUpperLimit"] = self.camera.AutoGainRawUpperLimit.GetValue()
        self.settings["AutoExposureTimeAbsLowerLimit"] = self.camera.AutoExposureTimeAbsLowerLimit.GetValue()
        self.settings["AutoExposureTimeAbsUpperLimit"] = self.camera.AutoExposureTimeAbsUpperLimit.GetValue()
        self.settings["AutoFunctionProfile"] = self.camera.AutoFunctionProfile.GetValue()
        self.settings["AutoFunctionAOIWidth"] = self.camera.AutoFunctionAOIWidth.GetValue()
        self.settings["AutoFunctionAOIHeight"] = self.camera.AutoFunctionAOIHeight.GetValue()
        self.settings["AutoFunctionAOIOffsetX"] = self.camera.AutoFunctionAOIOffsetX.GetValue()
        self.settings["AutoFunctionAOIOffsetY"] = self.camera.AutoFunctionAOIOffsetY.GetValue()

        self.settings["AutoFunctionAOIUsageIntensity"] = self.camera.AutoFunctionAOIUsageIntensity.GetValue()
        self.settings["AutoFunctionAOIUsageWhiteBalance"] = self.camera.AutoFunctionAOIUsageWhiteBalance.GetValue()
        ePrint(self.settings)
        time.sleep(2)

    def configureImageConverter(self):
        self.converter = pylon.ImageFormatConverter()
        self.converter.OutputOrientation = self.config["converter"]["Orientation"]
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
