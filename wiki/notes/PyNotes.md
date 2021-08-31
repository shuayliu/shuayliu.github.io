# Python Tricky Notes



## 读取EIS测量的数据

```python
import numpy as np
import os,sys

DATAFORMAT = {"tab":'\t',
              "space":' ',
              "comma":','
              }
DELIMITER = 'tab'
SKIPROWS = 1
POTENTIAL = 1
IMPORT_TYPE = "Zreal_Zimag"
FREQ_RANGE=[0,10000]


def loadData(filename,IMType = IMPORT_TYPE):
    if POTENTIAL == 0:
        data = np.loadtxt(filename, skiprows=SKIPROWS,
                          delimiter=DATAFORMAT[DELIMITER]).T
    elif POTENTIAL == 1:
        with open(filename, encoding='utf8') as _f:
            d = _f.read().splitlines()[SKIPROWS:]

    data = [_d.split(DATAFORMAT[DELIMITER]) for _d in d]
    potential = float(data[0][0])

    # 现在的数据是带有电位的data
    # 提取出电位，将剩下的转换为fre，zr，zi的数据格式
    data = np.array([_d[1:] for _d in data 
                        if FREQ_RANGE[0]<=float(_d[1])<FREQ_RANGE[1]],
                    dtype=np.float64).T


    if IMType == "Zreal_Zimag":
        try:
            freq,Zreal,Zimg = data[0:3]
        except:
            print("Data is not in right columns")
            return
    elif IMType == "Z_Phase":
        # 如果输入phase 和Z
        freq= data[0]
        Rad = data[2]
        ZMod= data[1]
        Zreal=ZMod * np.cos(Rad)
        Zimg =ZMod * np.sin(Rad) 
    
    return freq,Zreal,Zimg,potential
```



## 与pyDRTTool联合对EIS数据进行DRT处理

[F. Ciucci‘s Site](https://sites.google.com/site/drttools/download)

```python
import DRT_main as drt

def calculateDRT(filename):
    freq,Zreal,Zimg,potential =loadData(filename)
    eisObj = drt.Simple_run(drt.EIS_object(freq,Zreal,Zimg),
                    rbf_type='Gaussian',
                    data_used='Combined Re-Im Data',
                    induct_used=1,
                    der_used='1st order',
                    lambda_value=1E-3,
                    shape_control='FWHM Coefficient',
                    coeff=0.5)
    return potential,eisObj.out_tau_vec,eisObj.gamma
```

To run the Python version DRTtools, you need:

- Python 3
- Numpy, Pandas, Scipy, Matplotlib, PyQt5, and CVXPY

The DRTtools toolbox was tested and implemented on a Windows-based machine. 

Detailed installation instructions are available in the user's guide (also included with the standard distribution).

[1] T.H. Wan, M. Saccoccio, C. Chen, F. Ciucci, Influence of the Discretization Methods on the Distribution of Relaxation Times Deconvolution: Implementing Radial Basis Functions with DRTtools, Electrochimica Acta, 184 (2015) 483-499.

## batch 处理文件夹

```python
def batchCalculate(dirr):
    if not os.path.isdir(dirr):
        return
    else:
        print("data is dir")
        sPath = os.path.join(dirr,'result')
        if not os.path.isdir(sPath):
            os.mkdir(sPath)
        sys.stdout.write("#"*int(81)+'|')
        j=0
        dirlst = os.listdir(dirr)
        for file in dirlst:
            _filename = os.path.join(dirr,file)
            if os.path.isfile(_filename):
                potential,tau,gamma = calculateDRT(_filename)
                
                # Save file
                np.savetxt(os.path.join(sPath,"DRT_"+file),
                            X=np.array([tau,gamma]).T,
                            delimiter='\t',
                            header='Tau(s)\tGamma(Ohm)\n#Potential=%s'%potential,
                            comments='')

                j+=1
                sys.stdout.write('\r'+(j*80//len(dirlst))*'-'+'->|'+"\b")
```



## 去除重复 removeDuplicates

```python
def removeDuplicates(dirr):
    dirlst = os.listdir(dirr)
    
    nDir = os.path.join(dirr,'SPLITE')
    if not os.path.exists(nDir):
        os.mkdir(nDir)
    E_lst = []
    for file in dirlst:
        if os.path.isfile(os.path.join(dirr,file)):
            with open(os.path.join(dirr,file), encoding='utf8') as _f:
                _f.readline()
                d =_f.readline().split('=')[-1].replace('\n','')
            if not d in E_lst:
                E_lst.append(d)
                src =os.path.join(dirr,file).replace('\\','\\\\').replace('/','\\\\')
                dst =os.path.join(nDir,file).replace('\\','\\\\').replace('/','\\\\')
                # 针对Windows系统
                os.system('copy %s %s'%(src,dst))   

```

