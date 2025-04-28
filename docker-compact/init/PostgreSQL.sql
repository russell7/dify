-- sudo -iu postgres psql
CREATE USER dify SUPERUSER PASSWORD '<superuser_password>';
-- systemctl restart postgresql-15

-- drop database dify;
-- drop database dify_plugin;

-- 注意：COLLATE CTYPE 可能在不同的系统上不同，请根据实际情况修改。使用 \l 查看当前实例的编码名称。
CREATE DATABASE dify WITH OWNER = dify ENCODING = 'UTF8' LC_COLLATE = 'en_US.UTF-8' LC_CTYPE = 'en_US.UTF-8';
CREATE DATABASE dify_plugin WITH OWNER = dify ENCODING = 'UTF8' LC_COLLATE = 'en_US.UTF-8' LC_CTYPE = 'en_US.UTF-8';
