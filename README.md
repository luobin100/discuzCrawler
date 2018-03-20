# discuzCrawler
A python crawler of a Discuz forum that famous in China.  
  
### Prerequisite
* python2.7
* mysql
* redis
  
### File Structure
file | explanation
------------ | -------------
config.py | configuration file (set mysql,redis connection and username / password of this forum etc.)
networkOnly.py | do the job that fetch response.content to redis (network part job only). 
processRedisPage.py | parse the html that cached in redis and save the thread title, post to database respectively.
networkOnly_otherPages.py | like the `networkOnly.py` with the difference that this one crawl from thread page 2 to the last page and `networkOnly.py` only crawl the first thread page.
refactor.py | function library (means refactored from early codes).
  
### Usage  
1. Set the cofinguration in `config.py` file.
2. Run files in order `networkOnly.py` -> `processRedisPage.py` -> `networkOnly_otherPages.py` (make sure already created tables in mysql)  
``` sql
CREATE TABLE `TB_Titles` (
  `tid` varchar(50) CHARACTER SET utf8 NOT NULL,
  `title` varchar(500) CHARACTER SET utf8 DEFAULT NULL,
  `board` varchar(50) CHARACTER SET utf8 DEFAULT NULL,
  `errormsg` varchar(500) CHARACTER SET utf8 DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;


CREATE TABLE `TB_Posts` (
  `postid` varchar(50) CHARACTER SET utf8 DEFAULT NULL,
  `tid` varchar(50) CHARACTER SET utf8 DEFAULT NULL,
  `userId` varchar(50) CHARACTER SET utf8 DEFAULT NULL,
  `userName` varchar(50) CHARACTER SET utf8 DEFAULT NULL,
  `postsCount` int(11) DEFAULT NULL,
  `points` int(11) DEFAULT NULL,
  `accountCreatedDate` varchar(50) CHARACTER SET utf8 DEFAULT NULL,
  `postDateTime` varchar(50) CHARACTER SET utf8 DEFAULT NULL,
  `floorNum` int(11) DEFAULT NULL,
  `postStatus` varchar(500) CHARACTER SET utf8 DEFAULT NULL,
  `postMessage` varchar(20000) CHARACTER SET utf8 DEFAULT NULL,
  `locked` varchar(500) CHARACTER SET utf8 DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;


```
