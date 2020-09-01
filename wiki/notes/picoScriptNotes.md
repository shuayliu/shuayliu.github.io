# PicoScript手记

*unfinished*

文档对应PicoView & PicoScript 1.14.4版本

## Python version

### 获取显微镜模式

### Part A TMicroscopeMode   `int GetMicroscopeMode()`

- *modeSTM:* STM microscope mode. 
- *modeContactAFM:* ContactAFM microscope mode.
- *modeCSAFM:* CSAFM microscope mode.
- *modeForceModulation:* ForceModulation microscope mode.
- *modeDLFM:* DLFM microscope mode.
- *modeACAFM:* ACAFM microscope mode.
- *modeEFM:* EFM microscope mode.
- *modeKFMAM:* KFMAM microscope mode.
- *modeKFMFM:* KFMFM microscope mode.
- *modeHarmonic:* Harmonic microscope mode.
- *modeExpert:* Expert microscope mode.

#### 示例代码

```pyt
import picoscript
print "GetMode:", picoscript.GetMode( )
```



### 获取设备状态

#### Part A 一般参数值 `double GetStatus**()`   data type:TDoubleStatus

- *statusInputServo:*  returns the error signal input value for STM, AFM, and AC AFM. A value is returned every **200 ms**.
- *statusVec:* returns the Vec input value for STM, AFM, and AC AFM. A value is returned every ***200 ms***.
- *statusIec:* returns the Iec input value for STM, AFM, and AC AFM. A value is returned every **200 ms**.
- *statusFriction:* returns the Friction input value for STM, AFM, and AC AFM. A value is returned every **200 ms**.
- *statusBNC:* returns the BNC input value for STM, AFM, and AC AFM.ue allowed where the sweep stops upon reaching.  A value is returned every **200 ms**.
- *statusSum:* returns the Sum input value for STM, AFM, and AC AFM. A value is returned every **200 ms**.
- *statusRawDefl:* returns the RawDeflection input value for STM, AFM, and AC AFM. A value is returned every **200 ms**.
- *statusSpm2Aux:* returns the PicoPlus Aux input value for STM, AFM, and AC AFM. This input is located at the rear panel of the Head Electronics Box. A value is returned every **200 ms**.
-  *statusAux0:* returns the Surface Potential (SP)  input value for STM, AFM, and AC AFM for SPM 2 only. A value is returned every **200 ms.**
- *statusAux1:* returns the Aux1  input value for STM, AFM, and AC AFM for SPM 2 only. A value is returned every **200 ms.**
- *statusAux2:* returns the Aux2  input value for STM, AFM, and AC AFM for SPM 2 only. A value is returned every **200 ms**.
- *statusAux3:* returns the Aux 3  input value for STM, AFM, and AC AFM for SPM 2 only. A value is returned every **200 ms**.
- *statusAux4:* returns the Aux 4  input value for STM, AFM, and AC AFM for SPM 2 only. A value is returned every **200 ms**.
- *statusXSensor:* returns the X Sensor  input value for STM, AFM, and AC AFM for Closed loop. The return range is -10 to 10 V. A value is returned every **200 ms**.
- *statusYSensor:* returns the Y Sensor input value for STM, AFM, and AC AFM for Closed Loop. The return range is -10 to 10 V. A value is returned every **200 ms**.
-  *statusApproachPosition:* returns the Approach Position value for STM, AFM, and AC AFM. A value is returned every **200 ms**.
- *statusAmplitudeSetpoint:* returns the Amplitude Setpoint value for AC AFM. A value is returned every .
- *statusTopographyOffset:* returns the Topography  Offset value for STM, AFM, and AC AFM. This is the offset of the servorange in the main tab of the Servo dialog.
-  *statusTopographyRange:* returns the Topography  range value for STM, AFM, and AC AFM. This is the servorange in the main tab of the Servo dialog.
- *statusTimebase:* input change between two successive points which can then be used to trigger an output.
- *statusZPosition:* returns the Tip Position value for STM, AFM, and AC AFM. This is the tip postion in the servorange in the main tab of the Servo dialog. A value is returned every **200 ms** and can be read with the servo ON or OFF.
- *statusStageCurrentXPosition:* returns the current x-tip position.
- *statusStageCurrentYPosition:* returns the current y-tip position.
- *statusStageExpectedXPosition:* returns the expected x-tip position.
- *statusStageExpectedYPosition:* returns the expected y-tip position.
- *statusTipOpticalXPosition:* returns the current x-tip optical (camera view) position.
- *statusTipOpticalYPosition:* returns the current y-tip optical (camera view) position.

#### Part B 获取扫描状态参数 `int GetStatus**()`   data type:TIntStatus

- *statusApproachState:* returns ***immediately*** the Approach State (whether the tip is approaching or engaged) for STM, AFM, and AC AFM, where  0 is not approaching and 1 is approaching. 

-  *statusScanLine:* returns the scan line where the scan has stopped for STM, AFM, and AC AFM. Scan line DOES update during scanning. The following return behavior should be noted:

- - Scan lines are 0 index based. Thus, a resolution of 16 in X gives scan line limits of 0 to 15.
    - These scan line limits are only returned at the scan bottom and top turnarounds. For example, when the scan continues at the bottom and top of the scan area, the return values for scan line limits are 0 and 15, respectively.
    - When the scan stops at the bottom or top of the scan area, the return scan line is  one less than the mentioned limits. For example, for a scan which stops at the bottom, the return value is 1; and, for a stop at the top, the return value is 14.

- *statusScanPixel:* returns the pixel where the scan has stopped for STM, AFM, and AC AFM. Pixel DOES NOT update during scanning--updates when scan stops.

- *statusScanLineHeld:* returns the line which 'Hold Slow' holds the tip  for STM, AFM, and AC AFM. Returns -1 when Hold Slow is not active

#### Part C 功能和状态判断 ` double GetStatus**()`    data type:TBoolStatus

- *statusSPM2Supported:* returns whether the SPM system supports SPM2 for STM, AFM, and AC AFM.
- *statusXYClosedLoopSupported:* returns whether the SPM system supports XY closed loop for STM, AFM, and AC AFM.
- *statusZClosedLoopSupported:* returns whether the SPM system supports Z closed loop for STM, AFM, and AC AFM.
- *statusScanning:* returns whether a scan is in progress for STM, AFM, and AC AFM.
- *statusSpectroscopySweeping:* returns whether a Spectroscopy sweep is in progress for STM, AFM, and AC AFM.
- *statusControllerBooted:* returns whether controller is connected to PicoView for STM, AFM, and AC AFM.
- *statusPulsing:* returns whether pulse defined in the Servo dialog is in progress for STM, AFM, and AC AFM.
- *statusTuneSweeping:* returns whether AC manual or auto tune is in progress for STM, AFM, and AC AFM.
- *statusScanUp:* returns whether an up scan is in progress for STM, AFM, and AC AFM.
- *statusStageMoveInProgress:* returns whether stage tip movement is in progress for STM, AFM, and AC AFM.
- *statusStageExperimentInProgress:* returns whether stage experiment is in progress for STM, AFM, and AC AFM.
- *statusTipMoving:* returns whether tip is moving for STM, AFM, and AC AFM. Note, this does not apply to tip while scanning.
- *statusECSweepInProgress:* returns whether EC sweep is in progress.

#### 示例代码

```python
import picoscript
print "GetStatusScanLine:",picoscript.GetStatusScanLine()
```



### 获取扫描参数

#### Part A TDoubleScanParameter   `  double GetScanSize( )`

- *scanSize:* Reads the x and y scan range by the same amount. The range is limited by the scanner parameters. This value has meters for units. 
- *scanXOffset:* Reads x-postion of the reduced scan range within the maximum allowable scan range
- *scanYOffset:* Reads y-postion of the reduced scan range within the maximum allowable scan range
- *scanSpeed:* Reads the scan speed. There are only certain allowable scan speeds which are Max/n, where n = 1, 2,3...).
- *scanAngle:* Reads the orientation of the reduced scan range by rotating it in degrees. Positive values rotate the image area clockwise
- *scanXOverscan:* For the x-axis, scans a percentage of the viewable scan area. This region is not viewed in the image buffer.
- *ScanYOverscan:* For the y-axis, scans a percentage of the viewable scan area. This region is not viewed in the image buffer.
- *scanXServoIGain:* Applies integral gain to the closed loop x-sensor. This has the effect of controlling the feedbackloop based on its history
- *scanXServoPGain:* Applies Proportional gain to the closed loop x-sensor. This has the effect of controlling the feedbackloop based on its current status
- *scanYServoIGain:* Applies integral gain to the closed loop y-sensor. This has the effect of controlling the feedbackloop based on its history
- *scanYServoPGain:* Applies Proportional gain to the closed loop y-sensor. This has the effect of controlling the feedbackloop based on its current status
- *scanTipSpeed:* tip speed in meters/second when moved in x or y. Used with SetTipPositon function.

#### Part B TIntScanParameter    `  int GetScanSize( )`

- *scanXPixels:* The number of pixels for the X axis. The actual number of pixels is one greater than this value (eg, 512 pixels are coded as 511)..
- *scanYPixels:* The number of pixels for the Y axis. The actual number of pixels is one greater than this value (eg, 512 pixels are coded as 511)..
- *scanFrames:* Reads the number of frames which will be scanned.

#### Part C  TBoolScanParameter     `Bool GetScanSize( )`

- *scanTipLift:* Lifts the tip when the reduced scan area is moved more than half its X or Y length
- *scanHoldSlow:* Holds the tip in Y (tip doesn't move in the y-coordinate) and scans in x
- *scanXYServoActive:* Enables or disables the XY closed loop servo control.
- *scanAutoSave:* Enables or disables image autosave.

#### 示例代码

```python
import picoscript

print "ScanSize: ", picoscript.GetScanSize()
print "ScanXOffset: ", picoscript.GetScanXOffset()
print "ScanYOffset: ", picoscript.GetScanYOffset()
```





