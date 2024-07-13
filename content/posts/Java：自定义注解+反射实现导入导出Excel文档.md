---
title: Java：自定义注解+反射实现导入导出Excel文档

date: 2020-05-08
tags:
- 编程
- 后端
---



# 问题背景
最近遇到的需求：用户填写平台提供的模板文件（sample.xlsx），导入到平台中，代替填写表单/表格的动作。用户也可以将填好的表单/表格导出成Excel文件，便于以文档的形式存档或传输。
# 问题分析
从上述需求得出，这就是一个Excel文档与`Java Bean`对象互相转换的问题。

Excel文件的读写、操作，可以使用`Apache Poi`或其他开源库，在此不多说。主要问题是，当模板文件内容较为复杂，或者需要处理多个模板时，怎样能快速解析出文档的内容，与`Java Bean`的字段对应上呢？
**应用Java反射的原理，使用自定义注解 + 泛型，很容易实现灵活适配多个模板，并能快速支持模板的修改，便于扩展和维护。**

# 模板文件分析
分析模板文件，我发现可以将模板分为两种。
1. 表单式
![表单式](https://upload-images.jianshu.io/upload_images/6810620-edd21e42adeca658.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

内容行标、列标均确定，例如该表格B1固定为姓名的值，将内容解析成单个JavaBean对象。

2. 表格式
![表格式](https://upload-images.jianshu.io/upload_images/6810620-cd02b99b72e481f4.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

内容列固定，例如A列均为学号，应将除去表头外的每一行解析成一个JavaBean 对象，返回Java Bean对象的列表。

分析完毕，发现Java Bean 对象的某个字段的值与Excel文档单元格内容的对应关系就是行标 + 列标，那么我们只需要记录这个坐标，就能实现转换。
使用在字段上加注解的方式，简明易懂，并且很容易维护。下面给出实现代码。


# 实现
## 1、定义注解类

```java
@Target({ElementType.FIELD})
@Retention(RetentionPolicy.RUNTIME)
public @interface ExcelAnnotation {
    /**
     * 中文名称 label  
     */
    String cnName() default "";
    /**
     * 英文名称 对应到JavaClass上的类名
    
     */
    String enName() default "";
    /**
     *
     文件中的行标 - 从0开始计数
     */
    int rowIndex() default -1;
 
    int sheetIndex() default -1;
    /**
     *
     * 文件中的列标 - 从0开始计数
     */
    int columnIndex() default  -1;
}
```
注解用来说明字段对应的单元格工作簿序号、行标、列标等信息，以及
## 2、定义Java Bean
* 表单式对应的对象
```java
@Data
class Person{
  @ExcelAnnotation(rowIndex = 0,columnIndex = 1,cnName = "姓名")
  private String name;

  @ExcelAnnotation(rowIndex = 2,columnIndex = 1,cnName = "电话号码")
  private String phoneNum;
 ...
}
```
 * 表格式对应的对象
只需要定义列的中文名（cnName）,不需要定义行标
```java
@Data
class Student{
  @ExcelAnnotation(cnName = "学号")
  private String number;

  @ExcelAnnotation(cnName = "姓名")
  private String name;

  @ExcelAnnotation(cnName = "电话号码")
  private String phoneNum;
}
```
## 3、工具类实现写入和写出
定义Excel操作的工具类
`ExcelUtils.java`
```java
@Log4j2
public class ExcelUtils {


    public static <T> List<T> analysisExcelSheetAsTable(Sheet sheet,Class<T> clazz,int headerIndex) throws IntrospectionException {
        ArrayList<Row> rowContent = new ArrayList<>();
        TreeMap<Integer, Method> writeMethodTreeMap = new TreeMap<>();
        //  记录表头内容与
        HashMap<String,Integer> headerCnNameMap = new HashMap<>();
        // 默认的表头数据
        // 获取表头数据
        Row tableHeader = sheet.getRow(headerIndex);
        //
        int index = 0;
        for(Cell headerCell: tableHeader){
            String headerContent =   ExcelUtils.getCellFormatValue(headerCell).toString().trim();
            headerCnNameMap.put(headerContent,index);
            index++;
        }
        // 忽略第一行表头数据
        for (int i = (headerIndex+1); i < sheet.getPhysicalNumberOfRows(); i++) {
            rowContent.add(sheet.getRow(i));
        }
        for (Field field : clazz.getDeclaredFields()) {
            // 获取字段上的注解
            Annotation[] annotations = field.getAnnotations();
            if (annotations.length == 0) {
                continue;
            }
            for (Annotation an : annotations) {
                // 若扫描到ExcelAnnotation注解
                if (an.annotationType().getName().equals(ExcelAnnotation.class.getName())) {
                    // 获取指定类型注解
                    ExcelAnnotation excelAnnotation = field.getAnnotation(ExcelAnnotation.class);
                    try {
                        // 获取该字段的method方法
                        PropertyDescriptor pd = new PropertyDescriptor(field.getName(), clazz);
                        // 从头部获取cnName
                        if(headerCnNameMap.containsKey(excelAnnotation.cnName())){
                            writeMethodTreeMap.put(headerCnNameMap.get(excelAnnotation.cnName()), pd.getWriteMethod());
                        }

                    } catch (IntrospectionException e) {
                        throw e;
                    }
                }
            }
        }
        DataFormatter dataFormatter = new DataFormatter();
        List<T> resultList = new ArrayList<>();
        for (Row row : rowContent) {
            String rowValue = dataFormatter.formatCellValue(row.getCell(0));
            try {
                T model = clazz.newInstance();
                if (!StringUtils.isEmpty(rowValue)) {
                    for(int cellIndex: writeMethodTreeMap.keySet()){
                        if(row.getCell(cellIndex) != null){
                            Cell cell = row.getCell(cellIndex);
                            String value = ExcelUtils.getCellFormatValue(cell).toString();
                            writeMethodTreeMap.get(cellIndex).invoke(model, value);
                        }

                    }
                    resultList.add(model);
                }
            } catch (InstantiationException | IllegalAccessException | InvocationTargetException e) {
                e.printStackTrace();
            }

        }
        return resultList;
    }




    /**
     * 解析Excel表格内容 - 按照表格解析
     * @param sheet
     * @param ignoreRowNum 忽略的行数（表头）

     * @param <T>
     * @return
     */
    public static <T> List<T> analysisExcelSheetAsTable(Sheet sheet, int ignoreRowNum, Class<T> clazz) {
        ArrayList<Row> rowContent = new ArrayList<>();
        TreeMap<Integer, Method> writeMethodTreeMap = new TreeMap<>();
        // 从忽略的表头开始读
        for (int i = ignoreRowNum; i < sheet.getPhysicalNumberOfRows(); i++) {
            rowContent.add(sheet.getRow(i));
        }
        for (Field field : clazz.getDeclaredFields()) {
            // 获取字段上的注解
            Annotation[] annotations = field.getAnnotations();
            if (annotations.length == 0) {
                continue;
            }
            for (Annotation an : annotations) {
                // 若扫描到ExcelAnnotation注解
                if (an.annotationType().getName().equals(ExcelAnnotation.class.getName())) {
                    // 获取指定类型注解
                    ExcelAnnotation excelAnnotation = field.getAnnotation(ExcelAnnotation.class);
                    try {
                        // 获取该字段的method方法
                        PropertyDescriptor pd = new PropertyDescriptor(field.getName(), clazz);
                        writeMethodTreeMap.put(excelAnnotation.columnIndex(), pd.getWriteMethod());
                    } catch (IntrospectionException e) {
                        e.printStackTrace();
                    }
                }
            }
        }
        DataFormatter dataFormatter = new DataFormatter();
        List<T> resultList = new ArrayList<>();
        for (Row row : rowContent) {
            String rowValue = dataFormatter.formatCellValue(row.getCell(0));
            try {
                T model = clazz.newInstance();
                if (!StringUtils.isEmpty(rowValue)) {
                    // 遍历格子
                    int i = 0;
                    for (Cell cell : row) {

                        if (!writeMethodTreeMap.containsKey(i)) {
                            i++;
                            continue;
                        }
                        String value = ExcelUtils.getCellFormatValue(cell).toString();
                        writeMethodTreeMap.get(i).invoke(model, value);
                        i++;
                    }
                    resultList.add(model);
                }
            } catch (InstantiationException | IllegalAccessException | InvocationTargetException e) {
                e.printStackTrace();
            }

        }
        return resultList;
    }

    /**
     * 读取Cell
     *
     * @param cell
     * @return
     */
    public static Object getCellFormatValue(Cell cell)
    {
        Object cellValue;

        //判断cell类型
        switch (cell.getCellTypeEnum())
        {
            case NUMERIC:
            {
                cellValue = cell.getNumericCellValue();
                break;
            }
            case FORMULA:
            {
                //判断cell是否为日期格式
                if (DateUtil.isCellDateFormatted(cell))
                {
                    //转换为日期格式YYYY-mm-dd
                    cellValue = cell.getDateCellValue();
                }
                else
                {
                    //数字
                    cellValue = cell.getNumericCellValue();
                }
                break;
            }
            case STRING:
            {
                cellValue = cell.getRichStringCellValue().getString();
                break;
            }
            default:
                cellValue = "";
        }
        return cellValue;
    }
}

```
## 4、调用
在业务类（`Service`）中调用
* 调用仅为示范
```java
// 导入
 public void importExcelFile(InputStream inputStream){
        try (Workbook workbook = WorkbookFactory.create(inputStream)) {
           
            Person person= ExcelUtil.analysisExcelSheetAsForm(workbook.getSheetAt(0),Person.class);
            List<Student> students= ExcelUtil.analysisExcelSheetAsTable(workbook.getSheetAt(1),1,Student.class);
// 仅示范调用方式，可自行返回
        
        } catch (Exception ex) {
            log.error("Excel解析失败！",ex);
            throw new BusinessException("Excel解析失败！");
        }
    }

    //导出
    public void exportExcelFile(List<Student> students,Person person,HttpServletResponse httpServletResponse){
        //1、读取excel模板文件，作为本次下载的模板
        try(InputStream inputStream = new FileInputStream(templatePath);
            Workbook workbook = WorkbookFactory.create(inputStream)){
            httpServletResponse.setContentType("application/octet-stream");
            httpServletResponse.setHeader("Content-Disposition", "attachment;filename=test.xlsx");
            // 2.根据查询到的内容，填充Excel表格内容
            ExcelUtil.writeToWorkbookAsForm(person,workbook.getSheetAt(0));
            ExcelUtil.writeToWorkbookAsTable(students,workbook.getSheetAt(1,1,Student.class);
            workbook.write(httpServletResponse.getOutputStream());
        } catch (IOException | InvalidFormatException e) {
            e.printStackTrace();
        }

    }

```
这样就完成啦。
对于写入Excel和读取Excel的一些格式、编码/解码方式，我们可以放在通用配置里，也可以在注解类中增加项目来应对特殊需求。




# 
# 总结
本篇涉及知识
1、泛型
2、自定义注解 + `Java `反射
3、`Apache Poi`的使用


* 为什么使用泛型？
1、将**数据类型**和**算法**进行剥离是一种很常用的设计思路，可以帮助我们更好地开发出通用方法。
2、使用泛型（而不是包容万物的Object类型）使代码更为可读，并能规避编译错误，还可以对传入类型的上界、下界进行规定。（super/extends）

