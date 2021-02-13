## BACKGROUND：

AUTOLAB是瑞士万通（Metrohm）的一款电化学工作站，能实现恒压、恒流等稳态或交流法、瞬时法等暂态测量。标称电流挡位下限为10 nA，理论上可实现最低1 pA的电流分辨率。

AUTOLAB提供C#接口的SDK，以及官方的NI（National Instrument）编辑模板，可供用户调用。但由于1. 鄙组太穷，以及科研版权问题（如果用了会被起诉）；2. 后续要和另外一台设备协作，那台设备不提供NI接口。决定用自写简单程序调用其API实现简单功能。


## TRACE：


### 1. C# 动态链接库的调用问题：

SDK手册给了两种C#连接库的调用方式，其一（推荐）：使用能调用C# dll的语言，如VB之类。我毫无VB编程经验，但搜索到PythonIron可以使用，似乎可尝试？其二：COM接口。这个貌似是上个世纪的东西，看了一两天没看懂要怎么用，于是乎放弃了。

但由于Python GUI不会写，只会用一些简单脚本，还停留在cli阶段；外加对执行效率的考量，以及考虑到以后使用的方便性，决定认真解决下C/C++调用C#的问题，毕竟C/C++啥都能干，这个应该不会解决不了吧？


### 2. C/C++调用框架：


C/C++调用C#，除了要借用公共语言运行库（CLR），还要注意一个关键的问题：托管代码（unmanaged code）的问题。托管代码的调用不同于普通类库，按照我的理解，他有点像在虚拟机中运行，会被垃圾回收？所以不能用new产生新对象，而要用gcnew之类；C#与C/C++之间数据类型转换也是一个比较麻烦的点，二者之间需要进行数据类型转换，特别是传入路径char*的时候，容易出现生命周期问题。不过好在，具体csdn上有很多示例代码可供参考。

后续大概率会全部使用C/C++作为主要编程语言，而且linkToAUTOLAB只会作为其中一环节，所以调用路径为：linkTest.exe --> linkToAUTOLAB.dll --> EchoChemie.Autolab.Sdk.dll


在linkToAUTOLAB.dll中，导出类AUTOLAB和一些接口测试函数，以供调用。


类定义：
```c++
class __declspec(dllexport) AUTOLAB{

public:

  AUTOLAB();

  ~AUTOLAB();


  bool Connect(char* hdwStpFl, char* EbdxFl);

  bool Disconnect();

  bool LoadProcedure(char* pcdFl);

  bool Measure();

  bool IsConnected();

  bool IsMeasuring();

  bool SaveAs(char* svdfname);


private:

  msclr::gcroot< EcoChemie::Autolab::Sdk::Instrument^ >* autolab;

  msclr::gcroot< EcoChemie::Autolab::Sdk::IProcedure^ >* procedure;

};

```
这里借用了gcroot模板处理托管对象的类成员问题。


### 3. testCV函数的实现：


为了测试效果，写了一个testCV函数作为test code，该函数的功能是连接上仪器、读取某个写好的程序文件（cv），测试，保存测试结果。一般而言，如果该过程没问题，后续应该也没什么问题。


测试代码

```c++
bool testCV() {

char hdw[] = R"(C:\Program Files\Metrohm Autolab\Autolab SDK 1.11\Hardware Setup Files\PGSTAT204\HardwareSetup.xml)";

char xfile[] = R"(C:\Program Files\Metrohm Autolab\Autolab SDK 1.11\Hardware Setup Files\Adk.x)";

char cv[] = R"(C:\Program Files\Metrohm Autolab\Autolab SDK 1.11\Standard Nova Procedures\Cyclic voltammetry.nox)";


printf("\n开始进行CV测试：\nHardwareSetup File: %s ;\nEmbededFileToStart: %s; \n\n",hdw,xfile);


if (connetToAUTOLAB(hdw,xfile)) {

printf("\nAUTOLAB 连接成功，接下来开始测量...\n");


if (loadAndMeasure(cv))

printf("\n读取Procedure：\n %s \n\n", cv);

else {

printf("没有读取到Procedure:\n%s\n,看一下文件还在吗？",cv);

return false;

}


int duration = 1;

while (autolab->IsMeasuring()) {

Sleep(1000);

printf("\r%d s过去了，还没测完", ++duration);

}


char fname[64];

char t[64];

getTimeStr(t);

sprintf_s(fname, "Result-%s.nox",t );

printf("\r OK it's done........\n");

printf("\n结果保存在：当前文件夹下，名称为：%s\n", fname);

saveResult(fname);


autolab->Disconnect()? printf("\nAUTOLAB 成功断开\n"):MessageBoxA(NULL, "AUTOLAB 失联了，一定是哪里有问题", "ERROR", MB_OK + MB_ICONERROR);

return true;

}

else {

::MessageBoxA(NULL, "Cannot Connect to Autolab", "ERROR", MB_OK + MB_ICONERROR);

return false;

}

}

```

### 4. 实际测试：


仪器关闭时进行运行linkTest:


仪器打开时：



测量完成：



用官方测试软件打开Result文件内容：




## BUGS：

    日期显示还是有点问题。
    对AUTOLAB无法连接的异常还不能捕捉到（应该是c#抛出的异常，不太清楚要如何catch ？）


## REMARKS：

目前算是阶段性可行，后续用Qt5加上GUI。GUI框架已经写好了，等找个时间把两者缝起来。预计下一篇更新的时候就是GUI完成了。
