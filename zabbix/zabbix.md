# ZABBIX常用手册
### 删除ZABBIX历史记录
##### 编辑 clean_history.sql 文件
```
-- intervals in days
SET @history_interval = 7;
SET @trends_interval = 90;

DELETE FROM alerts WHERE (UNIX_TIMESTAMP(NOW()) - clock) > (@history_interval * 24 * 60 * 60);
DELETE FROM acknowledges WHERE (UNIX_TIMESTAMP(NOW()) - clock) > (@history_interval * 24 * 60 * 60);
DELETE FROM events WHERE (UNIX_TIMESTAMP(NOW()) - clock) > (@history_interval * 24 * 60 * 60);

DELETE FROM history WHERE (UNIX_TIMESTAMP(NOW()) - clock) > (@history_interval * 24 * 60 * 60);
DELETE FROM history_uint WHERE (UNIX_TIMESTAMP(NOW()) - clock) > (@history_interval * 24 * 60 * 60);
DELETE FROM history_str WHERE (UNIX_TIMESTAMP(NOW()) - clock) > (@history_interval * 24 * 60 * 60);
DELETE FROM history_text WHERE (UNIX_TIMESTAMP(NOW()) - clock) > (@history_interval * 24 * 60 * 60);
DELETE FROM history_log WHERE (UNIX_TIMESTAMP(NOW()) - clock) > (@history_interval * 24 * 60 * 60);

DELETE FROM trends WHERE (UNIX_TIMESTAMP(NOW()) - clock) > (@trends_interval * 24 * 60 * 60);
DELETE FROM trends_uint WHERE (UNIX_TIMESTAMP(NOW()) - clock) > (@trends_interval * 24 * 60 * 60);
```
##### 执行SQL
```
mysql zabbix -p ./clean_history.sql
```
##### 释放空间
执行完以上操作之后，你会发现磁盘空间并没有释放，还需要执行如下语句:
```
ALTER TABLE db.table ENGINE = InnoDB;
举例如下：
ALTER TABLE zabbix.alerts ENGINE = InnoDB;
```
##### 提示：
在执行该SQL语句"ALTER TABLE db.table ENGINE = InnoDB;"需要谨慎，因为会锁表。所以，建议在执行的时候尽量在数据空闲时间操作。
