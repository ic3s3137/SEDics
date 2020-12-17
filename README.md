# SEDics

## SEDics ##

#### 使用说明

社工字典生成工具，用于各种不同情境下的社工字典生成。

**原理**

用户通过不同元素集的组合自定义字典的生成规则，对规则中的不同元素组合，对元素字典中的元素进行排列组合生成规则对应的字典。比如

元素：a=["111","aaa","CCC"] b=["zip","bar"] 	规则：$a$$b$ 

对应字典为：["111.zip","aaa.zip","CCC.zip","111.bar","aaa.bar","CCC.bar"]

**模式**

字典的生成模式使用-t ｛type}指定，内置的模式有 backup,path,username,password四种，规则还比较简单，最好自行完善。

**元素**

构成规则中的基础元素。

元素字典存放于程序目录下的element目录下，根据参数-m {mode}指定的不同难度梯度，分别**叠加式**读取不同数量的元素条目，难度分为easy,normal,hard3个梯度。

类型元素字典：根据指定的 type 类型，自动读取{type}.txt和{type}.{name}.txt元素字典。

​	{type}.{name}.txt：{name}为规则中的元素名称。比如元素字典backup.ext.txt在规则中为$ext$，在插入条目到该元素字典前，要指定条目的难度梯度。

​	比如: 

​		[easy]

​		haha

​		dd

​		[normal]

​		hahahahahaha

​		dddddddddddd

​	{type}.txt中的元素条目使用[{name}.easy] ，[{name}.normal]来界定元素的名称和难度梯度。

全局元素字典：element.{name}.txt 为全局字典，如存在和{type}.{name}.txt相同的name，则合并元素并去重。

****社工元素：社工元素分为字符型和数字型，字符型使用-S指定，数字型-N指定，多个元素逗号分割****

**系统元素**

$TIME$：元素写法为$TIME:start,end:连接符$，用于生成指定日期的和日期之间连接符的动态元素。start和end的格式如$TIME:2019-09-01,2019-12-03:-$，不指定连接符时不使用日期连接符。

$DOMAIN$：若存在的话，为-d {domain} 中指定的目标域名根据变形后生成的域名元素。如 -d haha.com 会生成 hahacom，haha，haha_com等元素字典，具体根据-t指定的类型和内置规则决定。

**规则文件**

参数 -r {rulefile}指定要读取的规则，可指定多个规则，如-r myrule1,myrule2。若不指定，则默认规则文件为 {type}.rule。

自定义的规则文件请存放于rule目录下。

和元素字典一样，规则有3个难度梯度，分别为easy ,normal，hard ，难度梯度由参数 -m 指定，梯度越往后，规则越复杂，读取的元素字典条数越多，生成的字典越大。

example：

[easy]
$dirname$.$ext$

[normal]
$TIME:2019-09-01,2019-12-30:-$.$ext$

[hard]

$TIME:2019-01-01,2019-12-30:-$.$ext$

若参数-m为easy，只读取easy内的规则，若 -m为hard ,会同时读取easy，normal和hard中的所有规则。

其中，$dirname$元素对应的元素字典为{type}.dirname.txt

单条规则可使用#注释掉。

自动忽略规则中未定义的元素名称。

**过滤器**

使用参数 -f 指定，值为正则表达式，会把生成的字典中，符合过滤器的条目去除。

**保存**

使用 -o {savepath} 指定保存字典路径。



通过工作和日常的完善，让自己规则和元素字典足够成熟。
