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
在执行该SQL语句"ALTER TABLE db.table ENGINE = InnoDB;"需要谨慎，因为会锁表。所以，建议在执行的时候尽量在数据空闲时间操作。并且，在执行的时候遵循从小数据的表到大数据的表，此时会消耗大量的磁盘IO以及占用临时空间。
### 删除ZABBIX history_uint历史记录
上面的命令，在数据小的情况确实好使。但是...当你的数据到达一定的量的时候，可能效果极其的慢，这时候我们需要暴力一点。命令如下：
```
CREATE TABLE `history_uint_tmp` (
	`itemid`                 bigint unsigned                           NOT NULL,
	`clock`                  integer         DEFAULT '0'               NOT NULL,
	`value`                  bigint unsigned DEFAULT '0'               NOT NULL,
	`ns`                     integer         DEFAULT '0'               NOT NULL
) ENGINE=InnoDB;
CREATE INDEX `history_uint_1` ON `history_uint_tmp` (`itemid`,`clock`);

insert into history_uint_tmp select * from history_uint;
drop table history_uint;
alter table history_uint_tmp rename to history_uint;
```
谨慎骚操作，以上只适用于监控这种不重要的数据，其他环境操作需谨慎；
