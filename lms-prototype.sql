-- --------------------------------------------------------
-- Host:                         127.0.0.1
-- Server version:               8.0.32 - MySQL Community Server - GPL
-- Server OS:                    Win64
-- HeidiSQL Version:             11.3.0.6295
-- --------------------------------------------------------

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET NAMES utf8 */;
/*!50503 SET NAMES utf8mb4 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;


-- Dumping database structure for ghl
CREATE DATABASE IF NOT EXISTS `lms-prototype` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE `lms-prototype`;

-- Dumping structure for table ghl.al_carrier_std
CREATE TABLE IF NOT EXISTS `al_carrier_std` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` text,
  `conc_ppm` double DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


-- Dumping structure for table ghl.batches
CREATE TABLE IF NOT EXISTS `batch` (
  `id` int NOT NULL AUTO_INCREMENT,
  `batch_number` int DEFAULT NULL,
  `be_carrier_id` int DEFAULT NULL,
  `sample_count` int DEFAULT NULL,
  `be_carrier_bottle_init_g` double DEFAULT NULL,
  `be_carrier_bottle_final_g` double DEFAULT NULL,
  `al_carrier_id` int DEFAULT NULL,
  `al_carrier_bottle_init_g` double DEFAULT NULL,
  `al_carrier_bottle_final_g` double DEFAULT NULL,
  `AMS_lab` text,
  `comments` longtext,
  PRIMARY KEY (`id`),
  KEY `be_carrier_id` (`be_carrier_id`),
  KEY `al_carrier_id` (`al_carrier_id`),
  CONSTRAINT `fk_be_batch` FOREIGN KEY (`be_carrier_id`) REFERENCES `be_carrier_std` (`id`),
  CONSTRAINT `fk_al_batch` FOREIGN KEY (`al_carrier_id`) REFERENCES `al_carrier_std` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


-- Dumping structure for table ghl.be_carrier_std
CREATE TABLE IF NOT EXISTS `be_carrier_std` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` text,
  `conc_ppm` double DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


-- Dumping structure for table ghl.be_data
CREATE TABLE IF NOT EXISTS `be_al_data` (
  `id` int NOT NULL AUTO_INCREMENT,
  `sample_id` int DEFAULT NULL,
  `be_carrier_added_g` double DEFAULT NULL,
  `be_carrier_bottle_after_g` double DEFAULT NULL,
  `be_carrier_check` double DEFAULT NULL,
  `be_ratio` double DEFAULT NULL,
  `be_ratio_err` double DEFAULT NULL,
  `al_carrier_added_g` double DEFAULT NULL,
  `al_carrier_bottle_after_g` double DEFAULT NULL,
  `al_carrier_check` double DEFAULT NULL,
  `empty_lg_teflon_g` double DEFAULT NULL,
  `lg_teflon_and_sample_g` double DEFAULT NULL,
  `sample_wt_g` double GENERATED ALWAYS AS ((`lg_teflon_and_sample_g` - `empty_lg_teflon_g`)) STORED,
  `empty_sml_jar_g` double DEFAULT NULL,
  `sml_jar_and_aliquot_g` double DEFAULT NULL,
  `sml_jar_and_soln_g` double DEFAULT NULL,
  `aliquot_wt_g` double GENERATED ALWAYS AS ((`sml_jar_and_aliquot_g` - `empty_sml_jar_g`)) STORED,
  `soln_wt_g` double GENERATED ALWAYS AS ((`sml_jar_and_soln_g` - `empty_sml_jar_g`)) STORED,
  `al_ICP_ppm` double DEFAULT NULL,
  `al_ratio` double DEFAULT NULL,
  `al_ratio_err` double DEFAULT NULL,
  `comments` longtext,
  PRIMARY KEY (`id`),
  KEY `sample_id` (`sample_id`),
  CONSTRAINT `fk_sample_beal` FOREIGN KEY (`sample_id`) REFERENCES `sample` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS `_be10_al26_quartz` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `aliquot` longtext,
  `aliquot_wt_g` double DEFAULT NULL,
  `chem_lab` longtext,
  `chem_lab_date` date DEFAULT NULL,
  `chem_lab_id` longtext,
  `analyst` longtext,
  `Be_AMS_lab` longtext,
  `Be_AMS_date` date DEFAULT NULL,
  `Be_AMS_lab_id` longtext,
  `N10_atoms_g` double DEFAULT NULL,
  `delN10_atoms_g` double DEFAULT NULL,
  `N10b_subtracted_atoms` double DEFAULT NULL,
  `delN10b_subtracted_atoms` double DEFAULT NULL,
  `Be10_std` longtext,
  `qtz_Al_ppm` double DEFAULT NULL,
  `delqtz_Al_ppm` double DEFAULT NULL,
  `Al_AMS_lab` longtext,
  `Al_AMS_date` date DEFAULT NULL,
  `Al_AMS_lab_id` longtext,
  `N26_atoms_g` double DEFAULT NULL,
  `delN26_atoms_g` double DEFAULT NULL,
  `N26b_subtracted_atoms` double DEFAULT NULL,
  `delN26b_subtracted_atoms` double DEFAULT NULL,
  `Al26_std` longtext,
  `comments` longtext,
  `be_al_data_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `be_al_data_id` (`be_al_data_id`),
  CONSTRAINT `fk_data_conc` FOREIGN KEY (`be_al_data_id`) REFERENCES `be_al_data` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Dumping structure for table ghl.blank_data
CREATE TABLE IF NOT EXISTS `blank_data` (
  `id` int NOT NULL AUTO_INCREMENT,
  `batch_id` int DEFAULT NULL,
  `be_blank_carrier_g` double DEFAULT NULL,
  `be_blank_ratio` double DEFAULT NULL,
  `be_blank_ratio_unc` double DEFAULT NULL,
  `al_blank_carrier_g` double DEFAULT NULL,
  `al_blank_ratio` double DEFAULT NULL,
  `al_blank_ratio_unc` double DEFAULT NULL,
  `comments` longtext,
  PRIMARY KEY (`id`),
  KEY `batch_id` (`batch_id`),
  CONSTRAINT `fk_batch_blank` FOREIGN KEY (`batch_id`) REFERENCES `batch` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Dumping structure for table ghl.gel_images
CREATE TABLE IF NOT EXISTS `gel_image` (
  `id` int NOT NULL AUTO_INCREMENT,
  `batch_id` int DEFAULT NULL,
  `url_path` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `batch_id` (`batch_id`),
  CONSTRAINT `fk_batch_gelimg` FOREIGN KEY (`batch_id`) REFERENCES `batch` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


-- Dumping structure for table ghl.project
CREATE TABLE IF NOT EXISTS `project` (
  `id` int NOT NULL AUTO_INCREMENT,
  `project_name` text NOT NULL,
  `nsf_number` int DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Dumping structure for table ghl.samples
CREATE TABLE IF NOT EXISTS `sample` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` text,
  `batch_id` int DEFAULT NULL,
  `iced_sample_id` int DEFAULT NULL,
  `qtz_available_g` int DEFAULT NULL,
  `qtz_dissolved_g` double DEFAULT NULL,
  `age_est_a` double DEFAULT NULL,
  `prate_est` double DEFAULT NULL,
  `be_ratio_est` double DEFAULT NULL,
  `load_est_ug` double DEFAULT NULL,
  `hf_added_ml` double DEFAULT NULL,
  `comments` longtext,
  PRIMARY KEY (`id`),
  KEY `batch_id` (`batch_id`),
  CONSTRAINT `fk_batch_sample` FOREIGN KEY (`batch_id`) REFERENCES `batch` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


-- Dumping structure for table ghl.sample_project_match
CREATE TABLE IF NOT EXISTS `sample_project_match` (
  `id` int NOT NULL AUTO_INCREMENT,
  `sample_id` int NOT NULL DEFAULT '0',
  `project_id` int NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`),
  KEY `sample_id` (`sample_id`),
  KEY `project_id` (`project_id`),
  CONSTRAINT `fk_sample` FOREIGN KEY (`sample_id`) REFERENCES `sample` (`id`),
  CONSTRAINT `fk_project` FOREIGN KEY (`project_id`) REFERENCES `project` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

/*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;
/*!40014 SET FOREIGN_KEY_CHECKS=IFNULL(@OLD_FOREIGN_KEY_CHECKS, 1) */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40111 SET SQL_NOTES=IFNULL(@OLD_SQL_NOTES, 1) */;
