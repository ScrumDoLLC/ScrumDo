# I had created and ran a randomize_tokens command on the production DB that fixed this problem, so I'm commenting this out
# so everyone's RSS feeds don't break.

# ALTER TABLE `projects_project` ADD COLUMN `token` varchar(7) ;
# UPDATE projects_project SET token = substring(md5(rand()),-7) WHERE `token` IS NULL;
# ALTER TABLE `projects_project` MODIFY COLUMN `token` varchar(7) NOT NULL;