drop table if exists entries;
create table entries (
  id integer primary key autoincrement,
  author string not null,
  title string not null,
  text string not null,
  post_time timestamp not null
);
