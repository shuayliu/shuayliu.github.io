# Picoview 1.14 和AUTOLAB联用的代码方案

尝试各种方案之后，确定了如下的方案：

已实现的是：

> 探针移动到指定位置 -> 电化学测量

后续会实现的方案：

> 探针移动到指定位置 -> 做力曲线  -> 保持最大力值Hold at maximum force -> 电化学测量



## 0x00 前置准备：

1. Picoview 1.14及其对应Python版SDK；
2. Nova 1.11版本与官网SDK包   **！！注意：不同版本的Nova与SDK不通用**；
3. Python2.7 版本（e.g. Python(x,y)）及对应2.7版本的pythonnet包；





## 0x01 控制逻辑

仔细梳理后，确定EC进程实质上是作为AFM的子进程sub-routine进行，在每一个确定的Tip Positon进行测量。

流程图如下：

![image-20210820222657744](https://i.loli.net/2021/08/20/qry214iHDbKtk7T.png)

流程图代码：
```javascript
st=>start: Start
ed=>end: Finish
gen=>inputoutput: Generate Position Area
park=>operation: Park Tip to Position
saveFile=>operation: Save measured file
checkZPosition=>operation: Check and Adjust Z Position

subATLB=>subroutine: AUTOLAB Measurement

checkAllFinished=>condition: All Position Measured?


st->gen->checkAllFinished
checkAllFinished(yes)->ed

checkAllFinished(no)->park->checkZPosition
checkZPosition->subATLB(right)->saveFile->checkAllFinished
saveFile(right)->checkAllFinished
```







## 0x02 具体实现代码

实现代码包含两部分：

### class AUTOLAB()

```python
class AUTOLAB():
    
    def __init__(self,
                 sdk=R"C:\Program Files\Metrohm Autolab\autolabsdk\EcoChemie.Autolab.Sdk",
                 adx=R"C:\Program Files\Metrohm Autolab\autolabsdk\Hardware Setup Files\Adk.x")
 
    def disconnectAutolab(self):
    def setSDKandADX(self,sdk,adx)
 
    def isMeasuring(self) 
    def connectToAutolab(self,
                         hdw=R"C:\Program Files\Metrohm Autolab\autolabsdk\Hardware Setup Files\PGSTAT302N\HardwareSetup.FRA32M.xml")
   
    def save(self)
    def saveAs(self,saveName)
    
    def EIS(self,EISProc=R"E:\LSh\PicoView 1.14\scripts\STEP0-FRA.nox")
```



### batchParkTipToPositionArrayAndMeasureEC()函数

本函数的目的为将探针移动到指定位置后，进行电化学测量

```python
'''
description: 
param {*} xyPosArray
param {*} ECProc: EC Procedure location
return {*}
'''
def batchParkTipToPositionArrayAndMeasureEC(xyPosArray,
                                        ECProc = R"E:\LSh\PicoView 1.14\scripts\STEP0-FRA.nox"):
    CMDLOG(LOG_ENABLE,"Start batchParkTipToPositionArrayAndMeasureEC(),ECProc=%s"%ECProc)
    global autolab
    for xy in xyPosArray:
        CMDLOG(LOG_ENABLE,"Now Processing Pos(%d,%d)\n---------------------\n"%(xy[0],xy[1]))
        safeZPositionCheck()
        safeParkTipToPosition(xy[0],xy[1])
        autolab.measure(ECProc)
        # SaveFile
        filenameWithPositon = EC.appendSuffixToFilename(R"E:\LSh\LSh-EC\BatchTool_FRA.nox","_POSX%s-POSY%s"%(xy[0],xy[1]))
        autolab.saveAs(filenameWithPositon)
    
    autolab.disconnectAutolab()
    CMDLOG(LOG_ENABLE,"Finish batchParkTipToPositionArrayAndMeasureEC(),ECProc=%s\n\n"%ECProc)

```





### batchParkTipToMatrixAndMeasureEC() 函数：

本函数是函数```batchParkTipToPositionArrayAndMeasureEC()```封装版本

```python
def batchParkTipToMatrixAndMeasureEC(matrixX = 4,
                                     matrixY = 4,
                                     ECProc= R"E:\LSh\PicoView 1.14\scripts\STEP0-FRA.nox"):
    CMDLOG(1,"Let's Start")
    if not connectToAutolab(): return False
    ps.Connect()

    batchParkTipToPositionArrayAndMeasureEC(gridSpectroArea(matrixX,matrixY),ECProc)
    
    ps.Disconnect()
    CMDLOG(LOG_ENABLE,"Bye~Bye~\n\r")
    time.sleep(3)
```

### 

## 	其它安全函数



## Z位置看门狗 zWatchDog()

Z位置看门狗：在压针或者过远的时候通过调节样品盘来调节

```python
def zWatchDog(timeout=100):
    ps.Connect()
    CMDLOG(LOG_ENABLE,"Z Watchdog Start....\n")
    zSafeRange = ps.GetServoTopographyRange()/3
    startTime = time.clock()
    
    while (time.clock()-startTime) < timeout:
        CMDLOG(1,"-----------Monitoring since %d s ago-----------"%(time.clock()-startTime),'\r')
        try:
            while(abs(ps.GetStatusZPosition()) > zSafeRange):
                CMDLOG(LOG_ENABLE,"----DANGEROUS! MOVING Tip Away----",'\r')
                if ps.GetStatusZPosition() < 0:
                    time.sleep(0.3)
                    ps.MotorStepClose()
                    CMDLOG(1,"--------------Move 1 step close--------------",'\r')
                else:
                    time.sleep(0.3)
                    ps.MotorStepOpen()
                    CMDLOG(1,"--------------Move 1 step open--------------",'\r')
        except:
            CMDLOG(LOG_ENABLE,"EXCEPTION exit...\n")
            ps.Disconnect()
            return
        time.sleep(0.5)
        
    
    ps.Disconnect()
    CMDLOG(LOG_ENABLE,"Normally exit...\n")   
```





### 自动进针 checkApproachState()

自动进针：进针结束后，调整样品盘位置，以解决压针的问题

```python
def checkApproachState():
    # check approach or not
    if not ps.GetStatusApproachState():
        print("Start Approaching")
        ps.MotorApproach()
        ps.WaitForStatusApproachState(1)
        ps.WaitForStatusApproachState(0)
        print("Approaching Finished")

        zRange = ps.GetServoTopographyRange()
        while(abs(ps.GetStatusZPosition()) > zRange/3):
            print("Adjusting Z Positon")
            sleep(0.3)
            ps.MotorStepOpen()
```



