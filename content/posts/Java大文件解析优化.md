---
title: Java多线程：大文件解析优化

date: 2020-04-10
tags:
- 编程
- 后端
---
# 问题背景
>在应用系统中，常常需要建立文件管理系统，对存储在存储组件（常用有文件存储/数据库存储/对象存储等）中的物理文件、目录结构在应用数据库中进行逻辑建模，从而方便查询、读取和管理。

*这种设计体现了松耦合的特性，不论文件采取什么方式进行底层存储，应用层提供相同的接口，即使更换存储组件，上层接口不会改变，不影响到与其他模块的交互。*
应用系统为用户提供上传接口，该接口接收一个或多个压缩包（*.zip），返回文件存储路径。该接口为同步响应接口，响应时间不能太长，否则前端页面会失去响应，报超时异常。
当用户上传一个多目录结构、包含大批量文件的压缩包，处理速度会显著下降。对文件处理过程进行效率优化，能显著提高接口响应速度，带来更好的用户体验。
# 性能瓶颈
当前系统采用Amazon S3对象存储组件存储物理文件，MySQL数据库存储文件信息。
经过测试，现有解析并存储近2万个小文件的多目录压缩包，需要5分钟。

文件存储过程需要经历如下主要步骤：
![文件上传后主要步骤](https://upload-images.jianshu.io/upload_images/6810620-77b7bdc311fbcccd.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

文件存储步骤从上图可以看出，主要的时间开销为：

* 向存储组件写入文件耗时
* 建立数据库实体，写入数据库


分析业务逻辑代码，得到如下流程图：
![业务逻辑中存储逻辑](https://upload-images.jianshu.io/upload_images/6810620-a01fc3ba5d5573ce.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)


存储流程解决思路：将总任务拆解成独立、可重复执行的任务，多线程批量执行，减少与数据库交互次数。
**核心：改单线程为多线程，改单次操作为批量操作。**

# 拆解任务

经过分析，可以将需要处理的文件分为两类：目录和文件。
对于目录，只需要存储MySQL数据库记录，不需要存储至S3。
拆解任务的主要难点在于减少任务之间的时序依赖关系，而文件存储过程中存在的时序为：

* 目录层级
先向数据库写入父级目录，才能写入该目录下的子文件目录或子文件，以此类推。子文件实体的parentId字段记录父目录的id，存储路径为父目录地址 + 子文件名。
![文件实体](https://upload-images.jianshu.io/upload_images/6810620-05a1024001494817.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)


 模型如上面类图所示，数据库中不仅记录文件的大小、存储路径、类型等信息，同时保留层级结构。层级为树形，每一层目录信息需要依赖上一级而产生
* 去重
存储路径为唯一索引，在保存记录时需要先判重，再存储。

## 快速实现


```java
/**
递归解析文件夹
**/
private void handleDir(Long parentId, String parentPath, String dirPath, List<String> uploadRes) {  
	File[] filesAndDirs = new File(folderPath).listFiles();    
	for (File fileOrDir : filesAndDirs) {        
	if (fileOrDir.isFile()) {   
			//...向存储组件传输，并存储记录
	
  	} else {            
	   //建立父目录的文件实体           
		FileEntity fileEntity = FileEntity.builder().parentId(parentId)
													.path(parentPath + fileOrDir.getName()"/")                   
													.build();
		fileEntity = fileRepository.save(fileEntity);
      //递归调用       											     
		this.handleDir(fileEntity.getId(), fileEntity.getPath(), fileEntity.getPath(), uploadRes);        
		}    
	}
}

```
递归解析为单线程，该方法每次都需要执行判断逻辑，判断当前处理的是文件还是文件夹，并对每个目录文件都执行入库，再进行递归。
## 改进方案
将根目录下所有文件和目录一次性读取至内存中

```java
Collection<File> files = FileUtils.listFilesAndDirs(new 
File(testPath), TrueFileFilter.INSTANCE, 
TrueFileFilter.INSTANCE);
```

### 处理目录

目录层级按照深度归类，并按深度升序排列。在存储时，先存入父目录，再存子目录。


```java
TreeMap<Integer, List<File>> allDirs = 
dirs.stream().collect(Collectors.groupingBy(ParseTest::getFileDeep, TreeMap::new, Collectors.toList()));

/**
获取目录深度
**/
static int getFileDeep(File file){    
    String path = file.getAbsolutePath();    
    String[] deep = path.split("\\\\");    
    return deep.length;
}
```
Java8特性：将List使用lambda表达式转化成TreeMap
*为什么使用TreeMap？key值有序*
逐层处理：
存储目录时，将该目录实体与源文件绝对路径的映射存入缓存HashMap中。
只要不是第一层，都从缓存absolutePathMap中获取信息。存储到数据库时保留文件目录信息。
```java
       // 根据原文件的绝对路径，缓存该目录结构
        HashMap<String, FileEntity> absolutePathMap = new HashMap<>();
        for (int dirDeep : allDir.keySet()) {
            List<File> dirList = allDir.get(dirDeep);
            for (File dir : dirList) {
                // 获取该文件的父级目录绝对地址
                String parentAbsolutePath = dir.getAbsolutePath().substring(0, dir.getAbsolutePath().lastIndexOf("\\"));
                // 若不是第一层级，从缓存map中取出保存好的父目录信息
                if (dirDeep != allDirs.firstKey()) {
                    parentId = absolutePathMap.get(parentAbsolutePath).getId();
                    parentPath = absolutePathMap.get(parentAbsolutePath).getPath();
                }
                FileEntity fileEntity = FileEntity.builder().parentId(parentId).path(parentPath + dir.getName() + "/").build();
            
                fileEntity = fileRepository.save(fileEntity);
                absolutePathMap.put(dir.getAbsolutePath(), fileEntity);
            }

        }
```
遍历完成后，所有目录结构均已存入数据库中。

### 处理文件

剩余需要处理的是文件。文件所依赖的父目录信息已全部存入absolutePathMap中，文件和文件之间处理逻辑不存在时序依赖关系，可以引入多线程来进行分割处理。
#### Callable类
```java
@Log4j2
public class FileHandler implements Callable<List<String>> {

    // 分给本线程处理的文件
    private Collection<File> files;
    //存储父路径的地方
    HashMap<String, DentryDTO> absolutePathMap;
    public FileHandler(Collection<File> files,DentryDTO> absolutePathMap) {
        this.files = files；
        this.absolutePathMap = absolutePathMap;
    }
 
    @Override
    public List<String> call() {
    // 处理文件
        return res;
    }
```
 将需要处理的文件和所用到的absolutePathMap通过构造方法的参数传入。
* 若需要使用其他类，也通过构造参数传入。
* 使用Callable，该线程运行后会返回Future类型，是我们需要获取该线程的回调。

#### 多线程执行
```java
 	List<File> subList;
 	int batchSize = 500;
    // 计算运行规模（需要多少个线程）
 	int runSize = ((Double) (Math.ceil(singleFiles.size() * 1d / batchSize))).intValue();
 	ExecutorService executor = Executors.newFixedThreadPool(runSize);
     // 使用阻塞容器记录结果
 	BlockingQueue<Future<List<String>>> queue = new LinkedBlockingQueue<>();
	for (int i = 0; i < runSize; i++) {
      if ((i + 1) == runSize) {
           int startIndex = i * batchSize;
           subList = singleFiles.subList(startIndex, singleFiles.size());
        } else {
             int startIndex = i * batchSize;
              int endIndex = (i + 1) * batchSize;
              subList = singleFiles.subList(startIndex, endIndex);
        }
       FileHandler fileHandler = new FileHandler(subList,absolutePathMap);
            Future<List<String>> res = executor.submit(fileHandler);
            queue.add(res);
        }

        List<String> resAll = new ArrayList<>();
        int queueSize = queue.size();
        // 循环获取结果
        for (int i = 0; i < queueSize; i++) {
            resAll.addAll(queue.take().get());
         }
         executor.shutdown();
```
### 存储

在FileHandler中调用存储逻辑，也采用线程池方案。

# 注意事项
在linux环境下运行，需要注意路径分隔符与windows系统不同。应将代码中的“\\”使用File.separator代替。
线程数量可读取当前系统的CPU内核数量，从而容易取得更好的效率。

# 总结
在对任务进行恰当的逻辑分割后，很容易找到多线程的解决方案，充分利用CPU资源。
使用现有的线程池方案，避免创建过多空闲线程，能使效率更优。







