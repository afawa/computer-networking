# 网络实习
1、项目结构：

```
├── data
       ├── data //老师实地测量数据
       └── toy data //自己在家测量的数据
├── html //web应用前端实现
├── result //有关自制数据的说明
├── data_process.py //数据处理
├── locate.py //定位算法
├── locate_from_bkg.py //老师给的定位算法
├── test.py //本地运行定位算法
└── README.md 
```

2、本地运行定位算法

```
cmd>python test.py
```

3、本地访问前端，需要先

```
cmd> npm install -g local-cors-proxy
```

安装完成后

```
cmd> lcp --proxyUrl http://101.200.169.212:8080
```

proxy启动后，用浏览器打开html目录下的computer-network.html即可