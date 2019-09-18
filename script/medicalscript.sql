-- 用户表 
create table tusers(
    id int unsigned primary key auto_increment not null,
    name varchar(32) default '',
    birthday varchar(16),
    height decimal(5,2),
	weight decimal(5,2),
    gender enum('男','女','中性','保密') default '保密',
    role int unsigned default 0,-- 角色 0-病人 1-医生
	identity_id varchar(20),
	open_id  varchar(32),
	city varchar(16),
	province varchar(16),
    is_delete bit default 0
);