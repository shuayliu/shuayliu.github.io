#### 统一状态编码

```c++
enum COMMAND{
    EIS_QUERY = 0x002, AFM_QUERY = 0x004, ALL_QUERY = 0x006,
    EIS_READY = 0x007, AFM_READY = 0x009, ALL_READY = 0x00F,
    EIS_WAITE = 0x008, AFM_WAITE = 0x00A, ALL_WAITE = 0x011,
    ADV_PSSWD = 0xF66
}

```

#### PicoScript使用的Python27代码

```python


```



#### Nova 2.1.4 使用的.Net代码 v0.2 updateTime:2020.09.03

```c#
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Net;
using System.Net.Sockets;
using System.Threading;
using System.Runtime.InteropServices;

namespace socketClasses
{
    public enum COMMANDS:uint{ //定义状态代码，服务器与客户端使用约定的状态码进行通讯
        EIS_QUERY = 0x002, AFM_QUERY = 0x004, ALL_QUERY = 0x006,
        EIS_READY = 0x007, AFM_READY = 0x009, ALL_READY = 0x00F,
        EIS_WAITE = 0x008, AFM_WAITE = 0x00A, ALL_WAITE = 0x011,
    } 
        
    public class tcpClient{
        public tcpClient(){}

        //函数功能：AUTOLAB发送固定信号（EIS_READY）给Server
        public static bool SendEIS_READYToServer(String addr="127.0.6.1",UInt16 port=12580){
            IPAddress ip = IPAddress.Parse(addr); //解析IP地址
            Socket clientSocks = new Socket(AddressFamily.InterNetwork,
                SocketType.Stream, ProtocolType.Tcp);//初始化Socket连接
            //尝试连接至服务器（addr，port），如果无法连接则返回false
            try{
                clientSocks.Connect(new IPEndPoint(ip, port));
                Console.WriteLine("服务器已连接");
            }catch (Exception)            {
                Console.WriteLine("服务器连接失败");
                return false;
            }
            //连接至服务器，发送在COMMANDS中定义的通讯代码EIS_READY
            clientSocks.Send(Encoding.ASCII.GetBytes(COMMANDS.EIS_READY.ToString()));
            Console.WriteLine("Server端EIS状态已更新");
            clientSocks.Close();//发送完成，关闭连接，释放系统资源
            return true;
        }
        public static bool SendEIS_WAITEToServer(String addr="127.0.6.1",UInt16 port=12580){
            IPAddress ip = IPAddress.Parse(addr); //解析IP地址
            Socket clientSocks = new Socket(AddressFamily.InterNetwork,
                SocketType.Stream, ProtocolType.Tcp);//初始化Socket连接
            //尝试连接至服务器（addr，port），如果无法连接则返回false
            try{
                clientSocks.Connect(new IPEndPoint(ip, port));
                Console.WriteLine("服务器已连接");
            }catch (Exception)            {
                Console.WriteLine("服务器连接失败");
                return false;
            }
            //连接至服务器，发送在COMMANDS中定义的通讯代码EIS_WAITE
            clientSocks.Send(Encoding.ASCII.GetBytes(COMMANDS.EIS_WAITE.ToString()));
            Console.WriteLine("Server端EIS状态已更新");
            clientSocks.Close();//发送完成，关闭连接，释放系统资源
            return true;
        }

        public static String GetAFMStatusFromServer(String addr="127.0.6.1",UInt16 port=12580)
        {
            IPAddress ip = IPAddress.Parse(addr); //解析IP地址
            Socket clientSocks = new Socket(AddressFamily.InterNetwork,
                SocketType.Stream, ProtocolType.Tcp);//初始化Socket连接
            byte[] buffer = new byte[1024];
            //尝试连接至服务器（addr，port），如果无法连接则返回false
            try{
                clientSocks.Connect(new IPEndPoint(ip, port));
                Console.WriteLine("服务器已连接");
                clientSocks.Receive(buffer);
            }catch (Exception)            {
                Console.WriteLine("服务器连接失败");
                return "0";
            }
            //连接至服务器，发送在COMMANDS中定义的通讯代码AFM_QUERY
            clientSocks.Send(Encoding.ASCII.GetBytes(COMMANDS.AFM_QUERY.ToString()));
            clientSocks.Receive(buffer);
            Console.WriteLine("Server端EIS状态已更新");
            clientSocks.Close();//发送完成，关闭连接，释放系统资源
            return Encoding.ASCII.GetString(buffer);
        }
    }
}

```

