-- MySQL dump 10.13  Distrib 8.0.19, for Win64 (x86_64)
--
-- Host: localhost    Database: altyex
-- ------------------------------------------------------
-- Server version	9.4.0

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `AccountType`
--

DROP TABLE IF EXISTS `AccountType`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `AccountType` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) DEFAULT NULL,
  `dt_created` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `status` int NOT NULL DEFAULT '1',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `AccountType`
--

LOCK TABLES `AccountType` WRITE;
/*!40000 ALTER TABLE `AccountType` DISABLE KEYS */;
/*!40000 ALTER TABLE `AccountType` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Account`
--

DROP TABLE IF EXISTS `Account`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Account` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) DEFAULT NULL,
  `institution` varchar(100) DEFAULT NULL,
  `account_type_id` int DEFAULT NULL,
  `account_currency_id` int DEFAULT NULL,
  `client_id` int DEFAULT NULL,
  `dt_created` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `status` int NOT NULL DEFAULT '1',
  PRIMARY KEY (`id`),
  KEY `Account_AccountType_FK` (`account_type_id`),
  KEY `Account_AccountCurrency_FK` (`account_currency_id`),
  KEY `Account_Client_FK` (`client_id`),
  CONSTRAINT `Account_AccountCurrency_FK` FOREIGN KEY (`account_currency_id`) REFERENCES `AccountCurrency` (`id`),
  CONSTRAINT `Account_AccountType_FK` FOREIGN KEY (`account_type_id`) REFERENCES `AccountType` (`id`),
  CONSTRAINT `Account_Client_FK` FOREIGN KEY (`client_id`) REFERENCES `Client` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Account`
--

LOCK TABLES `Account` WRITE;
/*!40000 ALTER TABLE `Account` DISABLE KEYS */;
/*!40000 ALTER TABLE `Account` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `AccountBalance`
--

DROP TABLE IF EXISTS `AccountBalance`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `AccountBalance` (
  `id` int NOT NULL AUTO_INCREMENT,
  `account_id` int NOT NULL,
  `balance` float NOT NULL DEFAULT '0',
  `dt_created` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `status` int NOT NULL DEFAULT '1',
  PRIMARY KEY (`id`),
  KEY `AccountBalance_Account_FK` (`account_id`),
  CONSTRAINT `AccountBalance_Account_FK` FOREIGN KEY (`account_id`) REFERENCES `Account` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `AccountBalance`
--

LOCK TABLES `AccountBalance` WRITE;
/*!40000 ALTER TABLE `AccountBalance` DISABLE KEYS */;
/*!40000 ALTER TABLE `AccountBalance` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Category`
--

DROP TABLE IF EXISTS `Category`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Category` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) DEFAULT NULL,
  `description` varchar(100) DEFAULT NULL,
  `type` varchar(100) NOT NULL,
  `dt_created` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `status` int NOT NULL DEFAULT '1',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Category`
--

LOCK TABLES `Category` WRITE;
/*!40000 ALTER TABLE `Category` DISABLE KEYS */;
/*!40000 ALTER TABLE `Category` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Client`
--

DROP TABLE IF EXISTS `Client`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Client` (
  `id` int NOT NULL AUTO_INCREMENT,
  `tax_id` varchar(100) NOT NULL,
  `company_name` varchar(100) DEFAULT NULL,
  `industry` varchar(100) DEFAULT NULL,
  `email` varchar(100) DEFAULT NULL,
  `phone` varchar(100) DEFAULT NULL,
  `address` varchar(100) DEFAULT NULL,
  `fiscal_year_end` varchar(100) DEFAULT NULL,
  `dt_created` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `status` int NOT NULL DEFAULT '1',
  PRIMARY KEY (`id`),
  UNIQUE KEY `Client_UNIQUE` (`tax_id`)
) ENGINE=InnoDB AUTO_INCREMENT=14 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Client`
--

LOCK TABLES `Client` WRITE;
/*!40000 ALTER TABLE `Client` DISABLE KEYS */;
INSERT INTO `Client` VALUES (1,'stringggg','string','string','user@example.com','string','string','string','2026-01-06 09:43:21',99),(2,'string','string','string','user@example.com','string','string','string','2026-01-06 10:11:57',0),(10,'stringzonazona','string','string','user@example.com','string','string','string','2026-01-17 10:19:53',99),(12,'stringteste','string','string','user@example.com','string','string','string','2026-03-09 10:28:25',0);
/*!40000 ALTER TABLE `Client` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `CostCenter`
--

DROP TABLE IF EXISTS `CostCenter`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `CostCenter` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) DEFAULT NULL,
  `description` varchar(100) DEFAULT NULL,
  `dt_created` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `status` int NOT NULL DEFAULT '1',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `CostCenter`
--

LOCK TABLES `CostCenter` WRITE;
/*!40000 ALTER TABLE `CostCenter` DISABLE KEYS */;
/*!40000 ALTER TABLE `CostCenter` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Invoice`
--

DROP TABLE IF EXISTS `Invoice`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Invoice` (
  `id` int NOT NULL AUTO_INCREMENT,
  `invoice_number` varchar(100) DEFAULT NULL,
  `issue_date` date DEFAULT NULL,
  `due_date` date DEFAULT NULL,
  `amount` float DEFAULT NULL,
  `dt_created` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `status` int NOT NULL DEFAULT '1',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Invoice`
--

LOCK TABLES `Invoice` WRITE;
/*!40000 ALTER TABLE `Invoice` DISABLE KEYS */;
/*!40000 ALTER TABLE `Invoice` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Partner`
--

DROP TABLE IF EXISTS `Partner`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Partner` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) DEFAULT NULL,
  `description` varchar(100) DEFAULT NULL,
  `contact_info` varchar(100) DEFAULT NULL,
  `dt_created` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `status` int NOT NULL DEFAULT '1',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Partner`
--

LOCK TABLES `Partner` WRITE;
/*!40000 ALTER TABLE `Partner` DISABLE KEYS */;
/*!40000 ALTER TABLE `Partner` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Transaction`
--

DROP TABLE IF EXISTS `Transaction`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Transaction` (
  `id` int NOT NULL AUTO_INCREMENT,
  `transaction_date` timestamp NULL DEFAULT NULL,
  `description` varchar(100) DEFAULT NULL,
  `amount` float DEFAULT NULL,
  `category_id` int DEFAULT NULL,
  `account_id` int DEFAULT NULL,
  `transaction_status_id` int DEFAULT NULL,
  `partner_id` int DEFAULT NULL,
  `cost_center_id` int DEFAULT NULL,
  `invoice_id` int DEFAULT NULL,
  `dt_created` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `status` int NOT NULL DEFAULT '1',
  PRIMARY KEY (`id`),
  KEY `Transaction_Category_FK` (`category_id`),
  KEY `Transaction_Account_FK` (`account_id`),
  KEY `Transaction_Partner_FK` (`partner_id`),
  KEY `Transaction_CostCenter_FK` (`cost_center_id`),
  KEY `Transaction_Invoice_FK` (`invoice_id`),
  KEY `Transaction_TransactionStatus_FK` (`transaction_status_id`),
  CONSTRAINT `Transaction_Account_FK` FOREIGN KEY (`account_id`) REFERENCES `Account` (`id`),
  CONSTRAINT `Transaction_Category_FK` FOREIGN KEY (`category_id`) REFERENCES `Category` (`id`),
  CONSTRAINT `Transaction_CostCenter_FK` FOREIGN KEY (`cost_center_id`) REFERENCES `CostCenter` (`id`),
  CONSTRAINT `Transaction_Invoice_FK` FOREIGN KEY (`invoice_id`) REFERENCES `Invoice` (`id`),
  CONSTRAINT `Transaction_Partner_FK` FOREIGN KEY (`partner_id`) REFERENCES `Partner` (`id`),
  CONSTRAINT `Transaction_TransactionStatus_FK` FOREIGN KEY (`transaction_status_id`) REFERENCES `TransactionStatus` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Transaction`
--

LOCK TABLES `Transaction` WRITE;
/*!40000 ALTER TABLE `Transaction` DISABLE KEYS */;
/*!40000 ALTER TABLE `Transaction` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `AccountCurrency`
--

DROP TABLE IF EXISTS `AccountCurrency`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `AccountCurrency` (
  `id` int NOT NULL AUTO_INCREMENT,
  `code` varchar(100) DEFAULT NULL,
  `name` varchar(100) DEFAULT NULL,
  `dt_created` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `status` int NOT NULL DEFAULT '1',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `AccountCurrency`
--

LOCK TABLES `AccountCurrency` WRITE;
/*!40000 ALTER TABLE `AccountCurrency` DISABLE KEYS */;
/*!40000 ALTER TABLE `AccountCurrency` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ClientUsers`
--

DROP TABLE IF EXISTS `ClientUsers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ClientUsers` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) DEFAULT NULL,
  `email` varchar(100) DEFAULT NULL,
  `is_admin` tinyint(1) NOT NULL DEFAULT '0',
  `client_id` int DEFAULT NULL,
  `dt_created` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `status` int NOT NULL DEFAULT '1',
  PRIMARY KEY (`id`),
  KEY `ClientUsers_Client_FK_1` (`client_id`),
  CONSTRAINT `ClientUsers_Client_FK_1` FOREIGN KEY (`client_id`) REFERENCES `Client` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ClientUsers`
--

LOCK TABLES `ClientUsers` WRITE;
/*!40000 ALTER TABLE `ClientUsers` DISABLE KEYS */;
/*!40000 ALTER TABLE `ClientUsers` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `TransactionStatus`
--

DROP TABLE IF EXISTS `TransactionStatus`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `TransactionStatus` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) DEFAULT NULL,
  `description` varchar(100) DEFAULT NULL,
  `dt_created` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `status` int NOT NULL DEFAULT '1',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `TransactionStatus`
--

LOCK TABLES `TransactionStatus` WRITE;
/*!40000 ALTER TABLE `TransactionStatus` DISABLE KEYS */;
/*!40000 ALTER TABLE `TransactionStatus` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-03-09  8:00:18


-- ALTERATIONS 

ALTER TABLE altyex.Category add column client_id INT NULL;
ALTER TABLE altyex.CostCenter add column client_id INT NULL;
ALTER TABLE altyex.Partner add column client_id INT NULL;
ALTER TABLE altyex.Invoice add column client_id INT NULL;
ALTER TABLE altyex.TransactionStatus add column client_id INT NULL;

ALTER TABLE altyex.Category ADD CONSTRAINT Category_Client_FK FOREIGN KEY (client_id) REFERENCES altyex.Client(id);
ALTER TABLE altyex.CostCenter ADD CONSTRAINT CostCenter_Client_FK FOREIGN KEY (client_id) REFERENCES altyex.Client(id);
ALTER TABLE altyex.Partner ADD CONSTRAINT Partner_Client_FK FOREIGN KEY (client_id) REFERENCES altyex.Client(id);
ALTER TABLE altyex.Invoice ADD CONSTRAINT Invoice_Client_FK FOREIGN KEY (client_id) REFERENCES altyex.Client(id);
ALTER TABLE altyex.TransactionStatus ADD CONSTRAINT TransactionStatus_Client_FK FOREIGN KEY (client_id) REFERENCES altyex.Client(id);