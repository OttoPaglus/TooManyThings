CREATE TABLE IF NOT EXISTS `Thingstable` (
  `title` VARCHAR(100) NOT NULL,
  `deadline` VARCHAR(45) NOT NULL,
  `text` VARCHAR(400) NOT NULL,
  `id` INT NOT NULL,
  `level` INT NOT NULL,
  `isfinished` TINYINT NOT NULL,
  PRIMARY KEY (`id`))
