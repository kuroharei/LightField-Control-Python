from feinixsAPI import *
import matplotlib.pyplot as plt
import numpy as np
import csv
import time
from pyAndorSpectrograph.spectrograph import ATSpectrograph
from pyAndorSDK2 import atmcd, atmcd_codes, atmcd_errors



def scan(temp, wavelength, exposureTime, ystart, yend, start, end, step, com, axis, file_path):

    print("Initializing Camera")
    #Load libraries
    sdk = atmcd()
    spc = ATSpectrograph()
    codes = atmcd_codes

    #Initialize libraries
    shm = spc.Initialize("")
    print("Function Initialize returned {}".format(
        spc.GetFunctionReturnDescription(shm, 64)[1]))

    ret = sdk.Initialize("")
    print("Function Initialize returned {}".format(ret))

    if atmcd_errors.Error_Codes.DRV_SUCCESS == ret:
        if ATSpectrograph.ATSPECTROGRAPH_SUCCESS==shm:
        #Configure camera
            ret = sdk.SetTemperature(temp)
            print("Function SetTemperature returned {} target temperature {}".format(ret, temp))

            ret = sdk.CoolerON()
            print("Function CoolerON returned {}".format(ret))
            
            while ret != atmcd_errors.Error_Codes.DRV_TEMP_STABILIZED:
                time.sleep(5)
                (ret, temperature) = sdk.GetTemperature()
                print("Function GetTemperature returned {} current temperature = {}".format(
                ret, temperature), end="\r")

            print("")
            print("Temperature stabilized")

            ret = sdk.SetReadMode(codes.Read_Mode.MULTI_TRACK)
            print("Function SetReadMode returned {}".format(ret))
            
            ret = sdk.SetTriggerMode(codes.Trigger_Mode.INTERNAL)
            print("Function SetTriggerMode returned {}".format(ret))
            
            ret = sdk.SetAcquisitionMode(codes.Acquisition_Mode.ACCUMULATE)
            print("Function SetAcquisitionMode returned {}".format(ret))
            
            (ret, xpixels, ypixels) = sdk.GetDetector()
            print("Function GetDetector returned {} xpixel = {} ypixel = {} ".format(ret,xpixels,ypixels))

            ret = sdk.SetImage(1, yend - ystart + 1, 1, xpixels, ystart, yend)
            print("Function SetImage returned {}".format(ret))
            
            ret = sdk.SetExposureTime(exposureTime)
            print("Function SetExposureTime returned {}".format(ret))

        #Configure Spectrograph
            shm = spc.SetGrating(0, 1)
            print("Function SetGrating returned {}".format(
                spc.GetFunctionReturnDescription(shm, 64)[1]))

            (shm, grat) = spc.GetGrating(0)
            print("Function GetGrating returned: {} Grat".format(grat))

            shm = spc.SetWavelength(0, wavelength)
            print("Function SetWavelength returned: {}".format(
                spc.GetFunctionReturnDescription(shm, 64)[1]))

            (shm, wave) = spc.GetWavelength(0)
            print("Function GetWavelength returned: {} Wavelength: {}".format(
                spc.GetFunctionReturnDescription(shm, 64)[1], wave))

            (shm, min, max) = spc.GetWavelengthLimits(0, grat)
            print("Function GetWavelengthLimits returned: {} Wavelength Min: {} Wavelength Max: {}".format(
                spc.GetFunctionReturnDescription(shm, 64)[1], min, max))
            
            delaystage = DelayStage(com, 19200, "SMC", 0xCC, True)
            delaystage.home(axis)

        #Start Acquisition
            for pos in np.arange(start, end, step):
                delaystage.moveto(axis, pos)

                ret = sdk.StartAcquisition()
                print("Function StartAcquisition returned {}".format(ret))
                ret = sdk.WaitForAcquisition()
                print("Function WaitForAcquisition returned {}".format(ret))

                imageSize = xpixels
                (ret, arr, validfirst ,validlast) = sdk.GetImages16(1, 1, imageSize)
                print("Function GetImages16 returned {} first pixel = {} size = {}".format(ret, arr[0], imageSize))   

                (ret, xsize, ysize) = sdk.GetPixelSize()
                print("Function GetPixelSize returned {} xsize = {} ysize = {}".format(
                    ret, xsize, ysize))

                shm = spc.SetNumberPixels(0, xpixels)
                print("Function SetNumberPixels returned: {}".format(
                    spc.GetFunctionReturnDescription(shm, 64)[1]))

                shm = spc.SetPixelWidth(0, xsize)
                print("Function SetPixelWidth returned: {}".format(
                    spc.GetFunctionReturnDescription(shm, 64)[1]))

                (shm, calibrationValues) = spc.GetCalibration(0, xpixels)
                print("Function GetCalibration returned: {}, {}, {}, {},".format(
                    spc.GetFunctionReturnDescription(shm, 64)[1],
                    calibrationValues[0],
                    calibrationValues[1],
                    calibrationValues[2]))
                
                with open(file_path + "/" + str(pos).replace(".", "_") + "mm.csv", "w") as f:
                    writer = csv.writer(f)
                    writer.writerows(list(np.array([list(wavelength), list(arr)]).T))
                
            ret = sdk.ShutDown()
            print("Function Shutdown returned {}".format(ret))
            ret = spc.Close()
            print("Function Close returned {}".format(spc.GetFunctionReturnDescription(ret, 64)[1]))

        else:
            print("Cannot continue, could not initialize Spectrograph")
    else:
        print("Cannot continue, could not initialize camera")

if __name__=="__main__":
    scan(-80, 532, 1.0, 10, 30, 5.0, 15.0, 0.1, "COM4", "X", "D:/ChenLuozhou/20231113")