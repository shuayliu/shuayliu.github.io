# 力曲线处理步骤

Author: Jonah. Liu
Rev: A
Date: 20201211

> 本文适用软件
>
> 1. SPM控制软件：PicoView 1.14 
>
> 2. 处理库：ForceCurves.dll version 1.0.1.8
> 3. 处理软件 qForceCurve_light
> 4. OriginLab pro 9.0

## 基础使用

本部分介绍如何处理单条力曲线。

### 准备力曲线

从PicoView中将力曲线另存为.txt格式：

![image-20201211153557438](https://i.loli.net/2020/12/11/3lkdNouKMgO7iaS.png)

![image-20201211153742445](https://i.loli.net/2020/12/11/HshKMvn7W9ejNbt.png)



**导出后，不要对力曲线文件内容做任何预处理。**将所有要处理的数据存放到一个单独文件夹内。请勿在路径中包含中文名，这将会导致无法预期的错误。

*Note:*用记事本之类的软件打开，可以看到，txt文件的前164/165/166行为力曲线参数，从```Time(s) Distance(m) Force(V)``` 这一行开始为力曲线的数据。该行数是下一步处理的重要参数，会随着力曲线采用模式的不同而有差别。

![image-20201211154204502](https://i.loli.net/2020/12/11/b7mJ9UhErnuNx2M.png)

### 使用qForceCurveAnalysis进行处理

*Note:* qForceCurveAnalysis的核心库为```ForceCurve.dll```，请保证该文件存在，并且版本正确。

在打开程序前，须先在```config.ini```中设置参数：

![image-20201211181044663](https://i.loli.net/2020/12/11/v8beQc2BwHMoOny.png)

在**基本处理**中，只需修改```ForceConstant```力常数项和```Skiprows```文件间隔行项。``Skiprows``的数值就是上一章节查看txt文件确定的文件头行数，如果不确定具体多少，建议尝试164/165/166三个数值，数值错误时程序无法正常运行。

**注意：不要更改参数名称，包括但不限于空格、大小写等，修改时只修改等号后的内容**

打开程序：

![image-20201211154715870](https://i.loli.net/2020/12/11/TkXA9U42NLw8hMQ.png)

点击```选取```选择路径：例如，所有txt数据均整理在了```TMEP```文件夹下：

![image-20201211155025232](https://i.loli.net/2020/12/11/RzH3KYPN1kAxZhb.png)

确认后，程序下方空白位置会出现文件夹内所有的文件。如图中我们之前导出的力曲线文件```123.txt```:

![image-20201211155252012](https://i.loli.net/2020/12/11/yrm8QbSMxBNlc34.png)

点击```ok```程序便开始处理。

*Note：*如果文件过少，下方的进度条会出现BUG，此使无需理会，只要程序显示```完成```即代表已处理结束。

![image-20201211161338422](https://i.loli.net/2020/12/11/EPmhJ5OK8wikYrc.png)

处理结果在源文件目录下的```Result/```文件夹中，文件名与原始文件名保持一致。

![image-20201211161534427](https://i.loli.net/2020/12/11/Yz8gkW2tPbhO13y.png)

### 导入处理结果

将处理后的数据导入OriginLab进行做图，横坐标为```Distance(nm)``` ,纵坐标为```Force(nN)```

## 批量处理

volume模式的力曲线要首先导出为单条力曲线，然后再按照前一章节内容进行处理：

选中所有--> Save Selected Curves to Separate Files...

![image-20201211163333586](https://i.loli.net/2020/12/11/nl6O2ZWyaXm8FY1.png)



## OriginLab做统计图

统计图需要至少20条力曲线，并借助OriginLab的2D统计功能

### 1. 将*所有*数据导入为两列

选择OriginLab中的ImportMultiFiles导入功能，选取需要的文件进行导入**注意勾选Show Option Diaglog**：

![image-20201211163847495](https://i.loli.net/2020/12/11/ScDtHbyYMQq2ogs.png)



再弹出的对话框中，选择```Import Mode-> Start New Rows```

![image-20201211164004725](https://i.loli.net/2020/12/11/1Vf8XQOFa7L6BHi.png)

其余参数可默认。点击OK后，数据会自动导入为两列，如图所示（图中数据较少，真实的数据会更密集）。

![image-20201211164247808](https://i.loli.net/2020/12/11/HhxyNiopFUStWf1.png)



### 2. 进行二维直方统计



选中数据```Force(nN）```这一列后，选择二维统计。二维统计在 Statistics->Descriptive Statistics->2D Frequency Counting/Binning；如果第一次用，选择Open Dialog，也可以保存为Theme，直接选择相应的Theme。

![image-20201211164618647](https://i.loli.net/2020/12/11/g4HFQvBVez62DYC.png)

在弹出的对话框中参考下图设置参数

![image-20201211165604564](https://i.loli.net/2020/12/11/46is8fDL9cjTCer.png)

![image-20201211165149189](https://i.loli.net/2020/12/11/bOeswRVvhY4IZWS.png)

选择OK，会在OriginLab中出现一个新的WorkSheet，一般名称为TwoDBin* 。

在该Worksheet下，选择所有数据：

![image-20201211165255599](https://i.loli.net/2020/12/11/Jr3l6eOwEpHnPmQ.png)

做Contour->Colour Fill 图，设置参数基本不用修改：

![image-20201211165407921](https://i.loli.net/2020/12/11/k5EgrlCZXqJ7UsO.png)

结果：

![image-20201211165442621](https://i.loli.net/2020/12/11/F3w2HrTSEtOQk1A.png)

后续对图像进行优化：调整轴的显示范围、衬度等，可使图像更加美观。



## 图像精修和Ruptured Force 的确定

*待续*



## For Advanced User Note

OriginLab Code

> twoDBinning iy:=Col(B) -r 2 x.bin:=0 x.min:=-1 x.max:=15 x.inc:=0.1 y.bin:=0 y.min:=-0.5 y.max:=3 y.inc:=0.01;
> plotvm rowpos:=label label:=D colpos:=selcol1 xtitle:="Separation (nm)" ytitle:="Force (nN)" ztitle:=m0.1 irng:=TwoDBin1! ogl:=[%(page.longname$)]<new template:=TriContour>;